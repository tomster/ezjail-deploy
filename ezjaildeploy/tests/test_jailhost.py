from pytest import fixture
from ezjaildeploy.api import JailHost, JailSystem
from ezjaildeploy.examples.blueprints import UnboundJail, CryptoJailHost


@fixture
def config():
    return {
        'host': {
            'ip_addr': '10.0.1.1',
            'root_device': 'ada0'
        },
        'unbound': {
            'blueprint': 'ezjaildeploy.examples.blueprints.UnboundJail',
            'ip_addr': '10.0.1.2'
        },
        '_not_a_jail': {
            'foo': 23
        },
        'also_not_a_jail': {
            'bar': 'baz',
        }
    }


@fixture
def system(config):
    return JailSystem(**config)


def test_jailhost(system, config):
    assert isinstance(system.host, JailHost)
    assert system.host.ip_addr == config['host']['ip_addr']


def test_custom_jailhost(config):
    config['host']['blueprint'] = 'ezjaildeploy.examples.blueprints.CryptoJailHost'
    instance = system(config)
    assert isinstance(instance.host, CryptoJailHost)


def test_jailinstance(system, config):
    assert isinstance(system.jails['unbound'], UnboundJail)
    assert system.jails['unbound'].ip_addr == config['unbound']['ip_addr']


def test_jailinstance_has_ref_to_host(system, config):
    system.jails['unbound'].jailhost is system.host


def test_jailinstance_default(system):
    assert system.jails['unbound'].ports_to_install == ['dns/unbound']


def test_jailinstance_override_default(config):
    config['unbound']['ports_to_install'] = ['foo']
    instance = system(config)
    assert instance.jails['unbound'].ports_to_install == config['unbound']['ports_to_install']


def test_jailinstance_default_remote_root(system):
    assert system.jails['unbound'].fs_remote_root == '/usr/jails/unbound'


def test_jailinstance_override_remote_root(config):
    config['unbound']['fs_remote_root'] = 'foo'
    instance = system(config)
    assert instance.jails['unbound'].fs_remote_root == config['unbound']['fs_remote_root']


def test_underscore_skipped_as_jail(system):
    assert '_not_a_jail' not in system.jails


def test_jail_entry_without_blueprint_skipped(system):
    assert 'also_not_a_jail' not in system.jails
