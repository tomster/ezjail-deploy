from os import path
from filecmp import cmp
from pytest import raises, fixture
from ezjaildeploy.api import BaseJail
from ezjaildeploy.util import render_site_structure, render_template


@fixture
def fs_examples():
    import ezjaildeploy
    return path.abspath(path.join(path.dirname(ezjaildeploy.__file__),
            'examples'))


@fixture
def examples(request, tmpdir, fs_examples):
    return (str(tmpdir),
        fs_examples)


class DummyJail(BaseJail):

    @property
    def access_control(self):
        return '%s/16 allow' % self.ip_addr


def test_tempdir_created(examples):
    target_dir, fs_examples = examples
    fs_rendered = render_site_structure(path.join(fs_examples, 'unbound'),
        dict(ip_addr='192.168.0.1', access_control='10.0.1.0/16 allow'), target_dir)
    assert fs_rendered != path.join(fs_examples, 'unbound')


def test_subdirectories_created(examples):
    target_dir, fs_examples = examples
    fs_rendered = render_site_structure(path.join(fs_examples, 'unbound'),
        dict(ip_addr='192.168.0.1', access_control='10.0.1.0/16 allow'), target_dir)
    assert path.exists('%s/%s' % (fs_rendered, '/usr/local/etc'))


def test_string_replacement(examples):
    target_dir, fs_examples = examples
    fs_rendered = render_site_structure(path.join(fs_examples, 'unbound'),
        dict(ip_addr='192.168.0.1', access_control='10.0.1.0/16 allow'), target_dir)
    fs_unbound_conf = path.join(fs_rendered, 'usr/local/etc/unbound/unbound.conf')
    assert ('interface: 192.168.0.1' in open(fs_unbound_conf).read())


def test_computed_string_replacement(examples):
    """a jail instance can provide additional values computed from
    configuration values."""
    target_dir, fs_examples = examples
    jail = DummyJail(ip_addr='192.168.0.1', fs_local_root=path.join(fs_examples, 'unbound'))
    fs_rendered = render_site_structure(jail.fs_local_root, jail, target_dir)
    fs_unbound_conf = path.join(fs_rendered, 'usr/local/etc/unbound/unbound.conf')
    # eventhough we didn't provide it in the config explicitly, the
    # access control has been computed from the ip_addr and rendered:
    assert ('access-control: 192.168.0.1/16 allow' in open(fs_unbound_conf).read())


def test_render_copy(examples):
    """if the source is not a template, it is copied."""
    target_dir, fs_examples = examples
    fs_source = path.join(fs_examples, 'unbound/etc/rc.conf')
    fs_rendered = render_template(fs_source,
        target_dir,
        dict(ip_addr='192.168.0.1', access_control='10.0.1.0/16 allow'))
    assert fs_rendered.endswith('/rc.conf')
    assert (cmp(fs_source, fs_rendered))


def test_render_template(examples):
    """if the source is a template, it is rendered and the target file drops
    the `.tmpl` suffix."""
    target_dir, fs_examples = examples
    fs_rendered = render_template(path.join(fs_examples,
            'unbound/usr/local/etc/unbound/unbound.conf.tmpl'),
        target_dir,
        dict(ip_addr='192.168.0.1', access_control='10.0.1.0/16 allow'))
    assert fs_rendered.endswith('/unbound.conf')
    assert ('interface: 192.168.0.1' in open(fs_rendered).read())


def test_render_missing_key(examples):
    target_dir, fs_examples = examples
    with raises(KeyError):
        render_template(path.join(fs_examples,
                'unbound/usr/local/etc/unbound/unbound.conf.tmpl'),
            target_dir,
            dict())


def test_instance_from_dotted_name():
    from ezjaildeploy.examples.blueprints import UnboundJail
    from ezjaildeploy.util import instance_from_dotted_name
    assert instance_from_dotted_name('ezjaildeploy.examples.blueprints.UnboundJail') is UnboundJail


def test_dict_parser(fs_examples):
    from ezjaildeploy.util import get_config
    parsed_dict = get_config(path.join(fs_examples, 'jails.conf.sample'))
    assert parsed_dict['host']['ip_addr'] == '192.168.91.128'
