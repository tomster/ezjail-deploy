from collections import OrderedDict
from mock import MagicMock, patch
from pytest import fixture
from ezjaildeploy.api import BaseJail
from ezjaildeploy.stages import NameDescription, Step, Stage


class DummyNameDescription(NameDescription):
    '''You can provide the description as a doc string '''

    name = 'dummy'


@fixture
def name_description():
    return NameDescription()


def test_stage_explicit_name():
    bootstrap = NameDescription(name='bootstrap')
    assert bootstrap.name == 'bootstrap'


def test_stage_default_name(name_description):
    assert name_description.name == NameDescription.name


def test_stage_explicit_description():
    stage = NameDescription(description='''Nothing to see here''')
    assert stage.description == '''Nothing to see here'''


def test_stage_docstring_description(name_description):
    assert name_description.description == NameDescription.__doc__


@fixture
def bootstrap_command():
    return MagicMock()


@fixture
def configure_command():
    return MagicMock()


def real_command(foo='bar', baz=False):
    pass


def test_step_command():
    step = Step(command=real_command)
    assert step.command == real_command


def test_step_name_defaults_to_command_name():
    step = Step(command=real_command)
    assert step.name == 'real_command'


def test_step_uses_args(bootstrap_command):
    step = Step(command=bootstrap_command, args=['foo', True], kwargs=dict(blub=23))
    step()
    bootstrap_command.assert_called_once_with('foo', True, blub=23)


@fixture
def bootstrap_stage(bootstrap_command, configure_command):
    return Stage(name='bootstrap',
        steps=[
            Step(name='install', command=bootstrap_command, args=['foo', True], kwargs=dict(blub=23)),
            Step(name='configure', command=configure_command),
        ])


def test_assemble_stage_from_steps(bootstrap_stage, bootstrap_command, configure_command):
    bootstrap_stage()
    bootstrap_command.assert_called_once_with('foo', True, blub=23)
    configure_command.assert_called_once_with()


@fixture
def update_command():
    return MagicMock()


@fixture
def jail(bootstrap_stage, update_command):

    class DummyJail(BaseJail):

        stages = OrderedDict(
            bootstrap=bootstrap_stage,
            update=Step(name='update', command=update_command, kwargs=dict(backup_data=True))
        )

    return DummyJail(ip_addr='127.0.0.1')


def test_assemble_jail_from_stages(jail):
    assert jail.name == 'dummy'
    assert jail.stages.keys() == ['bootstrap', 'update']


def test_init_jail_stages(jail, bootstrap_stage, bootstrap_command, configure_command, update_command):
    jail.init()
    bootstrap_command.assert_called_once_with('foo', True, blub=23)
    configure_command.assert_called_once_with()
    update_command.assert_called_once_with(backup_data=True)


def test_execute_single_stage(jail, bootstrap_stage, bootstrap_command, configure_command, update_command):
    assert not update_command.called
    jail.execute_stage(name='bootstrap')
    assert bootstrap_command.called
    assert configure_command.called
    assert not update_command.called


def test_executing_second_stage_also_executes_first(jail, bootstrap_stage, bootstrap_command, configure_command, update_command):
    jail.execute_stage(name='update')
    assert bootstrap_command.called
    assert configure_command.called
    assert update_command.called


def test_skip_completed_stages(jail, bootstrap_stage, bootstrap_command, configure_command, update_command):
    with patch.object(bootstrap_stage, 'has_run', lambda: True):
        jail.execute_stage(name='update')
        assert not bootstrap_command.called
        assert not configure_command.called
        assert update_command.called
