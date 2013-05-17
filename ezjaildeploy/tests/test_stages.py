from collections import OrderedDict
from mock import MagicMock, patch
from pytest import fixture
from ezjaildeploy.api import BaseJail
from ezjaildeploy.stages import Step, Stage


@fixture
def mocked_step_bootstrap():
    return MagicMock()


@fixture
def mocked_step_configure():
    return MagicMock()


@fixture
def mocked_step_update():
    return MagicMock()


@fixture
def mocked_stage_bootstrap(mocked_step_bootstrap, mocked_step_configure):
    return Stage(name='bootstrap',
        steps=[
            Step(name='install',
                command=mocked_step_bootstrap,
                args=['foo', True], kwargs=dict(blub=23)),
            Step(name='configure', command=mocked_step_configure),
        ])


@fixture
def jail(mocked_stage_bootstrap, mocked_step_update):

    class DummyJail(BaseJail):

        stages = OrderedDict(
            bootstrap=mocked_stage_bootstrap,
            update=Stage(name='update',
                steps=[Step(name='verify',
                    command=mocked_step_update,
                    kwargs=dict(backup_data=True))]
            )
        )
    return DummyJail(ip_addr='127.0.0.1')


@fixture
def stage(jail):
    return jail.stages['update']


@fixture
def step(stage):
    return stage.steps['verify']


def real_command(foo='bar', baz=False):
    pass


def test_step_command():
    step = Step(command=real_command)
    assert step.command == real_command


def test_step_name_defaults_to_command_name():
    step = Step(command=real_command)
    assert step.name == 'real_command'


def test_step_uses_args(mocked_step_bootstrap):
    step = Step(command=mocked_step_bootstrap, args=['foo', True], kwargs=dict(blub=23))
    step()
    mocked_step_bootstrap.assert_called_once_with('foo', True, blub=23)


def test_assemble_stage_from_steps(mocked_stage_bootstrap, mocked_step_bootstrap, mocked_step_configure):
    mocked_stage_bootstrap()
    mocked_step_bootstrap.assert_called_once_with('foo', True, blub=23)
    mocked_step_configure.assert_called_once_with()


def test_assemble_jail_from_stages(jail):
    assert jail.name == 'dummy'
    assert jail.stages.keys() == ['bootstrap', 'update']


def test_init_jail_stages(jail, mocked_stage_bootstrap, mocked_step_bootstrap, mocked_step_configure, mocked_step_update):
    jail.init()
    mocked_step_bootstrap.assert_called_once_with('foo', True, blub=23)
    mocked_step_configure.assert_called_once_with()
    mocked_step_update.assert_called_once_with(backup_data=True)


def test_execute_single_stage(jail, mocked_stage_bootstrap, mocked_step_bootstrap, mocked_step_configure, mocked_step_update):
    assert not mocked_step_update.called
    jail.execute_stage(name='bootstrap')
    assert mocked_step_bootstrap.called
    assert mocked_step_configure.called
    assert not mocked_step_update.called


def test_executing_second_stage_also_executes_first(jail, mocked_stage_bootstrap, mocked_step_bootstrap, mocked_step_configure, mocked_step_update):
    jail.execute_stage(name='update')
    assert mocked_step_bootstrap.called
    assert mocked_step_configure.called
    assert mocked_step_update.called


def test_skip_completed_stages(jail, mocked_step_update, mocked_step_bootstrap, mocked_step_configure):
    with patch.object(jail.stages['bootstrap'], 'has_run', lambda: True):
        jail.execute_stage(name='update')
        assert not mocked_step_bootstrap.called
        assert not mocked_step_configure.called
        assert mocked_step_update.called


def test_stages_have_their_own_steps(jail):
    assert not jail.stages['bootstrap'].steps is jail.stages['update'].steps


def test_stage_references_its_jail(jail):
    assert jail.stages['update'].__jail__ is jail


def test_step_references_its_stage(jail):
    assert jail.stages['bootstrap'].steps['install'].__stage__ is jail.stages['bootstrap']
    assert jail.stages['update'].steps['verify'].__stage__ is jail.stages['update']


def test_marking_as_completed_sets_has_run(jail):
    stage = jail.stages['bootstrap']
    assert not stage.has_run()
    stage._mark_as_completed()
    assert stage.has_run()


def test_stage_snapshot_name(stage):
    assert stage._snapshot_name == '002-update'


def test_step_snapshot_name(step):
    assert step._snapshot_name == '002-update-001-verify'
