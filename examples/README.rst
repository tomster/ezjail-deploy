This directory contains tested and working examples. You should be able to run them simply by providing a custom ``jails.conf`` for your host environment. The following examples assume that you're working from a local copy of the ``examples`` directory that contain this README and have SSH access to a FreeBSD Host.

To get started, create a minimal version of ``jails.conf`` like so::

    [host]
    ip_addr = 192.168.91.128

Obviously, you'll need to replace the value for ``ip_addr`` with that of your jail host. 

Bootstrapping
=============

In order for ``ezjail-deploy`` to work, the following requirements must be met on the jail host:

 * ``sudo``, ``rsync`` and ``ezjail`` must be installed
 * SSH access for an account with sudo privileges

If you're host already meets these requirements or if you want to provide them manually, you can skip to the next section ''Deploying a simple jail''.

Otherwise, ``ezjail-deploy`` provides a convenience command ``bootstrap`` which does the following:

 * creates an admin user
 * configures SSH access
 * installs and configures ``sudo``, ``rsync`` and ``ezjail``

However, ``bootstrap`` itself still has some requirements of its own which you must provide manually:

 * ``sshd`` is up and running on ``ip_addr``
 * ``RootLogin`` is enabled (in ``/etc/ssh/sshd_config``)

Then ``cd`` into the examples directory and::

    # ezjail-deploy bootstrap


Deploying a simple jail
=======================

Either way, you now should be able to ssh into the host and run ezjail-admin::

    # ssh 192.168.91.128
    [...]
    $ sudo ezjail-admin -v
    ezjail-admin v3.2
    Usage: ezjail-admin [archive|config|console|create|delete|install|list|restore|update] {params}

Now you're ready to deploy the first example. First, exit the ssh shell again - from now on we're going to do everything remotely, afterall :-)::

    $ exit

Now add the following lines to your ``jails.conf``::

    [simple]
    ip_addr = 192.168.91.128

then run::

    # ezjail-deploy init simple

It will now create and start a jail instance named ``simple``, the existence of which you should be able to verify using the ``list-jails`` command::

    # exjail-deploy list-jails

However, since this jail doesn't do anything useful, let's get rid of it before moving on. To that end type::

    # exjail-deploy destroy simple

After answering ``YES`` to the confirmation dialog, the jail will have vanished. See for yourself::

    # exjail-deploy list-jails


Deploying a nameserver jail
===========================

Now, let's move on to an example that actually provides a pre-configured, useful feature: a simple forwarding and caching nameserver using the excellent ``unbound`` daemon. To do so simply rename the ``[simple]`` section in ``jails.conf`` to ``[unbound]``, so that your its contents now looks like this::

    [host]
    ip_addr = 192.168.91.128

    [unbound]
    ip_addr = 192.168.91.128

Note, that by virtue of the new jail's name matching a blueprint definition inside ``blueprints.py`` that jail instance is already associated with it. If you don't want to name your jail instance like its blueprint, you could do so and refer to the blueprint it should use explicitly like so::

    [nameserver]
    blueprint = UnboundJail
    ip_addr = 192.168.91.128

Then run::

    # ezjail-deploy init unbound

This will:

 * create a jail named ``unbound`` listening on the ip address of the jail host
 * install ``dns/unbound`` from ports
 * configure it to listen on the local network
 * enable it and start it up,

 If all went well, you now should be able to run queries against it::

    # dig @192.168.91.128 github.com

If you look at the actual blueprint you will notice that all that was necessary for this were two lines of configuration::

    [unbound]
    ip_addr = 192.168.91.128

five lines of code::

     class UnboundJail(BaseJail):
        ports_to_install = ['dns/unbound']

        @property
        def access_control(self):
            return '%s.0/16 allow' % '.'.join(self.ip_addr.split('.')[:3])

and a file tree consisting of a bunch of files::

    etc/rc.conf                                # enabling unbound daemon
    usr/local/etc/unbound/unbound.conf.tmpl    # unbound configuration
    var/db/ports/unbound/options               # port configuration
    var/db/ports/openssl/options
    var/db/ports/libiconv/options
    var/db/ports/perl/options

Also note, that if you don't like how this blueprint computes the access control you have two options three override this behavior.

Firstly, you could simple edit the ``access_control`` method in ``blueprints.py``.

Secondly, you could subclass the ``UnboundJail`` class and override the ``access_control`` method.

Or thirdly, you could simply override the return value of that method by adding an alternative value in ``jails.conf``::

    [unbound]
    ip_addr = 192.168.91.128
    access_control = 192.168.91.0/24


TODO:
 * example of two instances using the same blueprint (i.e. two nginx instances)
 * example using custom ``configure``
 * example using custom ``update``
 * example without config file (only 'hard coded' blueprints file)
 * example of one blueprint using config data of another instance (i.e. varnish pointing to nginx)
