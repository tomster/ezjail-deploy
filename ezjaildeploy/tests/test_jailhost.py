from pytest import fixture
from ezjaildeploy.api import JailHost, JailSystem
from ezjaildeploy.examples.blueprints import UnboundJail


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
    }


@fixture
def system(config):
    return JailSystem(**config)


def test_jailhost(system, config):
    assert isinstance(system.host, JailHost)
    assert system.host.ip_addr == config['host']['ip_addr']


def test_jailinstance(system, config):
    assert isinstance(system.jails['unbound'], UnboundJail)
    assert system.jails['unbound'].ip_addr == config['unbound']['ip_addr']


def test_jailinstance_default(system):
    assert system.jails['unbound'].ports_to_install == ['dns/unbound']


def test_jailinstance_overridedefault(config):
    config['unbound']['ports_to_install'] = ['foo']
    instance = system(config)
    assert instance.jails['unbound'].ports_to_install == config['unbound']['ports_to_install']


def test_jailinstance_default_remote_root(system):
    assert system.jails['unbound'].fs_remote_root == '/usr/jails/unbound'


def test_jailinstance_overrid_remote_root(config):
    config['unbound']['fs_remote_root'] = 'foo'
    instance = system(config)
    assert instance.jails['unbound'].fs_remote_root == config['unbound']['fs_remote_root']
