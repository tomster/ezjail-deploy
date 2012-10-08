from os import path
from filecmp import cmp
from tempfile import mkdtemp
from shutil import rmtree
from ezjaildeploy.util import render_site_structure, render_template


def setup_examples():
    import ezjaildeploy
    return path.abspath(path.join(path.dirname(ezjaildeploy.__file__), '../examples'))


def  test_tempdir_created(examples):
    fs_rendered = render_site_structure(path.join(examples, 'unbound'), dict(ip_addr='192.168.0.1'))
    assert fs_rendered != path.join(examples, 'unbound')
    return fs_rendered


def  test_subdirectories_created(examples):
    fs_rendered = render_site_structure(path.join(examples, 'unbound'), dict(ip_addr='192.168.0.1'))
    assert path.exists('%s/%s' % (fs_rendered, '/usr/local/etc'))
    return fs_rendered


def  test_string_replacement(examples):
    fs_rendered = render_site_structure(path.join(examples, 'unbound'), dict(ip_addr='192.168.0.1'))
    fs_unbound_conf = path.join(fs_rendered, 'usr/local/etc/unbound/unbound.conf')
    assert ('interface: 192.168.0.1' in open(fs_unbound_conf).read())
    return fs_rendered


def test_render_copy(examples):
    """if the source is not a template, it is copied."""
    target_dir = mkdtemp()
    fs_source = path.join(examples, 'unbound/etc/rc.conf')
    fs_rendered = render_template(fs_source,
        target_dir,
        dict(ip_addr='192.168.0.1'))
    assert fs_rendered.endswith('/rc.conf')
    assert (cmp(fs_source, fs_rendered))
    return target_dir


def test_render_template(examples):
    """if the source is a template, it is rendered and the target file drops the `.tmpl` suffix."""
    target_dir = mkdtemp()
    fs_rendered = render_template(path.join(examples, 'unbound/usr/local/etc/unbound/unbound.conf.tmpl'),
        target_dir,
        dict(ip_addr='192.168.0.1'))
    assert fs_rendered.endswith('/unbound.conf')
    assert ('interface: 192.168.0.1' in open(fs_rendered).read())
    return target_dir


if __name__ == '__main__':
    rmtree(test_string_replacement(setup_examples()))
