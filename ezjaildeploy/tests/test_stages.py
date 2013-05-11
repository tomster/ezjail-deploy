from mock import MagicMock
from pytest import fixture
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


def test_assemble_stage_from_steps(bootstrap_command, configure_command):
    stage = Stage(name='bootstrap',
        steps=[
            Step(name='install', command=bootstrap_command, args=['foo', True], kwargs=dict(blub=23)),
            Step(name='configure', command=configure_command),
        ])
    stage()
    bootstrap_command.assert_called_once_with('foo', True, blub=23)
    configure_command.assert_called_once_with()
