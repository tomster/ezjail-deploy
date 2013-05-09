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
