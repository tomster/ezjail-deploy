import inspect
from os import path
from shutil import rmtree
from collections import OrderedDict
from fabric import api as fab
from fabric.contrib.project import rsync_project
from ezjailremote import fabfile as ezjail

from util import render_site_structure


class JailHost(object):

    jailzfs = None
    ip_addr = None
    sshd_port = '22'
    install_ports = True
    install_from = 'pkg_add'

    def __init__(self, blueprints=None, config=dict()):
        """ config needs to contain at least one entry named 'host' which defines
        the jail host.
        any other entries that don't start with an underscore are treated as jail definitions.
        """
        self.config = config
        for key, value in config.get('host', dict()).items():
            setattr(self, key, value)

        if blueprints is None:
            from ezjailremote import api  # use examples instead
            blueprints = api

        self.available_blueprints = OrderedDict()
        for name in dir(blueprints):
            obj = getattr(blueprints, name)
            if inspect.isclass(obj) and issubclass(obj, BaseJail):
                if obj.name:
                    obj_name = obj.name
                else:
                    obj_name = obj.__name__.split('Jail')[0].lower()
                self.available_blueprints[obj_name] = obj

        self.jails = OrderedDict()
        for jail_name in set(config.keys()).union(set(self.available_blueprints.keys())):
            if jail_name.startswith('_') or jail_name == 'host':
                continue
            if jail_name in self.available_blueprints:
                jail_factory = self.available_blueprints[jail_name]
            else:
                try:
                    jail_factory = getattr(blueprints, config['jail_name']['blueprint'])
                except KeyError:
                    jail_factory = BaseJail
            self.jails[jail_name] = jail_factory(jailhost=self, name=jail_name, **config.get(jail_name, dict()))

    def bootstrap(self):
        # run ezjailremote's basic bootstrap
        ezjail.bootstrap(primary_ip=self.ip_addr)
        fab.sudo('pkg_add -r rsync')

    def install(self):
        ezjail.install(source=self.install_from, jailzfs=self.jailzfs, p=self.install_ports)


class BaseJail(dict):
    """A dict-like representation of a to-be-created or already existing jail instance.

        It provides three methods: create, configure and update which it expects to be run
        from a fabfile with a connection to the jail host.

        ``create`` and ``configure`` are expected to be run as-is, whereas ``extra_configure``
        (which is called by ``configure`` at the end) and ``update`` are expected to be overridden
        by any subclass.

    """

    name = ""
    ctype = None
    sshd = False
    ip_addr = None
    fs_local_root = None
    fs_remote_root = None
    preparehasrun = False
    ports_to_install = []
    jailhost = None

    def __getitem__(self, attr):
        try:
            return super(BaseJail, self).__getitem__(attr)
        except KeyError:
            try:
                return getattr(self, attr)
            except AttributeError:
                raise KeyError

    def __setitem__(self, key, value, force=False):
        if force:
            super(BaseJail, self).__setitem__(key, value)
        else:
            raise KeyError

    def __init__(self, **config):
        """
        Instantiate it with arbitrary parameters, but the following are mandatory:

        :param name: name of the jail
        :param: ip_addr: its IP address
        :param sshd: if True, an admin user will be created using the name and default ssh key of the user
            calling the fabfile and sshd will be configured and run inside the jail. Set this to False if
            you want to create a jail with a private IP which should not be accessible from outside the jailhost.
        :param ports_to_install: a list of strings denoting any ports that should be installed during ``configure``.
            The names are expected to be relative to ``/usr/ports``, i.e. ``lang/python``.
        :param fs_local_root: local path to a directory tree which will be uploaded to the root of the new jail during ``configure``.
            If None, a local path with the name of the jail relative to the location of the file containing the instance
            of thsi class is assumed.
            One use-case for this is to provide port configuration files in ``/var/db/ports/*/options`` which allows the ports
            installation to run without user-intervention.
        :param fs_remote_root: path to the jail, defaults to ``/usr/jails/NAMEOFJAIL``.
        :param ctype: passed as ``-type`` to ``ezjail-admin create``
        """
        for key, value in config.items():
            try:
                setattr(self, key, value)
            except AttributeError:
                self.__setitem__(key, value, force=True)
        # if we didn't get an explict name, set a default:
        if not self.name:
            self.name = self.__class__.__name__.split('Jail')[0].lower()
        # if we didn't get an explict root, set a default:
        if self.fs_local_root is None:
            self.fs_local_root = '%s/' % path.join(path.abspath(path.dirname(inspect.getfile(self.__class__))), self.name)
        if self.fs_remote_root is None:
            self.fs_remote_root = '/usr/jails/%s' % self.name

    def create(self):
        ezjail.create(self.name, self.ip_addr, ctype=self.ctype, sshd=self.sshd)

    def upload(self):
        if path.exists(self.fs_local_root):
            fab.sudo('rm -rf /tmp/%s' % self.name)
            fs_rendered = render_site_structure(self.fs_local_root, self)
            rsync_project('/tmp/%s/' % self.name, '%s/' % fs_rendered,
                extra_opts='--perms --executability -v --super')
            fab.sudo('rsync -rav /tmp/%s/ /usr/jails/%s/' % (self.name, self.name))
            fab.sudo('rm -rf /tmp/%s' % self.name)
            rmtree(fs_rendered)

    def prepare(self):
        # upload site root (it might contain port configuration)
        self.upload()
        # install ports
        for port in self.ports_to_install:
            self.console('make -C /usr/ports/%s install' % port)
        self.configure()
        self.preparehasrun = True

    def configure(self):
        pass

    def update(self):
        pass

    def destroy(self):
        return ezjail.destroy(self.name)

    def console(self, command):
        """ execute the given command inside the jail by calling ezjail-admin console.
        This is particularly useful for jails w/o sshd and/or a public IP
        """
        return fab.sudo("""ezjail-admin console -e "\"%s %s"\"""" % (command, self.name))
