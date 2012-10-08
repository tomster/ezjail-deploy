from os import path
from filecmp import cmp
from tempfile import mkdtemp
from shutil import rmtree
from ezjaildeploy.util import render_site_structure, render_template


def pytest_funcarg__examples(request):
    def setup():
        import ezjaildeploy
        fs_tempdir = mkdtemp()
        return (fs_tempdir,
            path.abspath(path.join(path.dirname(ezjaildeploy.__file__),
                '../examples')))

    def teardown(examples):
        fs_tempdir, fs_examples = examples
        rmtree(fs_tempdir)

    return request.cached_setup(setup=setup,
        teardown=teardown, scope='function')


def  test_tempdir_created(examples):
    target_dir, fs_examples = examples
    fs_rendered = render_site_structure(path.join(fs_examples, 'unbound'),
        dict(ip_addr='192.168.0.1'), target_dir)
    assert fs_rendered != path.join(fs_examples, 'unbound')


def  test_subdirectories_created(examples):
    target_dir, fs_examples = examples
    fs_rendered = render_site_structure(path.join(fs_examples, 'unbound'),
        dict(ip_addr='192.168.0.1'), target_dir)
    assert path.exists('%s/%s' % (fs_rendered, '/usr/local/etc'))


def  test_string_replacement(examples):
    target_dir, fs_examples = examples
    fs_rendered = render_site_structure(path.join(fs_examples, 'unbound'),
        dict(ip_addr='192.168.0.1'), target_dir)
    fs_unbound_conf = path.join(fs_rendered, 'usr/local/etc/unbound/unbound.conf')
    assert ('interface: 192.168.0.1' in open(fs_unbound_conf).read())


def test_render_copy(examples):
    """if the source is not a template, it is copied."""
    target_dir, fs_examples = examples
    fs_source = path.join(fs_examples, 'unbound/etc/rc.conf')
    fs_rendered = render_template(fs_source,
        target_dir,
        dict(ip_addr='192.168.0.1'))
    assert fs_rendered.endswith('/rc.conf')
    assert (cmp(fs_source, fs_rendered))


def test_render_template(examples):
    """if the source is a template, it is rendered and the target file drops
    the `.tmpl` suffix."""
    target_dir, fs_examples = examples
    fs_rendered = render_template(path.join(fs_examples,
            'unbound/usr/local/etc/unbound/unbound.conf.tmpl'),
        target_dir,
        dict(ip_addr='192.168.0.1'))
    assert fs_rendered.endswith('/unbound.conf')
    assert ('interface: 192.168.0.1' in open(fs_rendered).read())
