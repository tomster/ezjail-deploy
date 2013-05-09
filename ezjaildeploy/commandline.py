"""Usage:
    ezjail-deploy [options] (bootstrap|install|list-blueprints|list-jails)
    ezjail-deploy [options] (init|upload|prepare|configure|update|destroy|debug) [JAIL]...

Deploy a jail host and/or jail(s).

Options:
    -b , --blueprints FILE   path to the blueprint python file [default: ./blueprints.py]
    -c, --config FILE        path to config file [default: ./jails.conf]
    -h, --help               show this message
    -v, --verbose            show more output


Commands:
    boostrap: prepare a remote jail host via SSH and install ezjail
    install: install ezjail (without bootstrapping)
    list-blueprints: display a list of all available blueprints
    init: call the `create`, `prepare` and `update`` methods of all given jails.
        if no jail is specified, *all* jails are targetted.

    upload: renders and uploads the local file tree

    update: assumes that the jail's `create` and `prepare` methods have already run
        and executes their `update` method. if no jail is specified, *all* jails are
        targetted. it should be able to run a jail's `update` method more than once
        during the lifetime of a jail.
"""

import sys
from docopt import docopt
from fabric import api as fab
from os import path
from ezjaildeploy.util import get_config
from ezjaildeploy.api import JailSystem


def main(args, **kwargs):
    # parse the command line arguments
    arguments = docopt(__doc__)

    # parse the configuration
    fs_config = arguments['--config']
    config = get_config(fs_config)

    # inject custom blueprints into sys.path
    if arguments.get('--blueprints') is None:
        blueprints = None
    else:
        fs_dir, fs_blueprint = path.split(path.abspath(arguments['--blueprints']))
        sys.path.insert(0, fs_dir)
        blueprints = __import__(fs_blueprint.strip('.py'))

    # inject location of the config file so jails can resolve relative paths
    config['_fs_config'] = path.dirname(path.abspath(fs_config))

    # instantiate the jail system
    jailsystem = JailSystem(_blueprints=blueprints, **config)
    jailhost = jailsystem.host

    # 'point' fabric to the jail host
    if jailhost.public_ip_addr is not None:
        ip_addr = jailhost.public_ip_addr
    else:
        ip_addr = jailhost.ip_addr

    fab.env['host_string'] = ip_addr
    fab.env['host'] = ip_addr
    fab.env['hosts'] = [ip_addr]
    fab.env['port'] = jailhost.sshd_port

    # execute the bootstrap and/or install command
    if arguments['bootstrap']:
        jailhost.bootstrap()
    if arguments['install'] or arguments['bootstrap']:
        jailhost.install()
        exit()

    if arguments['list-blueprints']:
        for name, blueprint in jailsystem.jails.items():
            if arguments['--verbose']:
                description = blueprint.__doc__
            else:
                try:
                    description = blueprint.__doc__.split('\n')[0]
                except AttributeError:
                    description = ""
            print '%s: %s' % (name, description)
        exit()

    if arguments['list-jails']:
        fab.sudo('ezjail-admin list')
        exit()

    jail_name = arguments['JAIL'][0]
    jail = jailsystem.jails[jail_name]

    # the main entry points
    if arguments['init']:
        jail.init()
    elif arguments['update']:
        jail.update()
    elif arguments['destroy']:
        jail.destroy()
    # the remainder are usually only used for debugging
    elif arguments['upload']:
        jail._upload()
    elif arguments['prepare']:
        jail._prepare()
    elif arguments['configure']:
        jail.configure()
    elif arguments['debug']:
        jail._debug()
