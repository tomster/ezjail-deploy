from pytest import fixture
from ezjaildeploy.stages import NameDescription


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
