from pytest import raises
from ezjaildeploy.api import BaseJail


class DummyJail(BaseJail):

    @property
    def access_control(self):
        return '%s/16 allow' % self.ip_addr


def test_property_dict_access():
    jail = DummyJail(ip_addr='10.0.1.1')
    assert jail['access_control'] == '10.0.1.1/16 allow'


def test_property_dict_access_override():
    """setting a value will override a jails property of the same name"""
    jail = DummyJail(ip_addr='10.0.1.1', access_control='foo')
    assert jail['access_control'] == 'foo'


def test_key_error_raised():
    jail = DummyJail()
    with raises(AttributeError):
        jail['foo']


def test_attribute_error_raised():
    jail = DummyJail()
    with raises(AttributeError):
        jail.foo


def test_item_access_via_property():
    jail = DummyJail(foo='bar')
    assert jail.foo == 'bar'
