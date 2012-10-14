"""Usage:
    ezjail-deploy [options] (bootstrap|install|list-blueprints|list-jails)
    ezjail-deploy [options] (init|upload|prepare|configure|update|destroy) [JAIL]...

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
from mrbob.parsing import parse_config


def main():
    # parse the command line arguments
    arguments = docopt(__doc__)

    # parse the configuration
    fs_config = arguments['--config']
    config = dict()
    if path.exists(fs_config):
        config = parse_config(fs_config)['variables']

    # instantiate host and jails
    fs_dir, fs_blueprint = path.split(path.abspath(arguments['--blueprints']))
    sys.path.insert(0, fs_dir)
    blueprints = __import__(path.splitext(fs_blueprint)[0])
    # inject location of the config file so jails can resolve relative paths
    config['_fs_config'] = path.dirname(path.abspath(fs_config))
    jailhost = getattr(blueprints, config.get('host', dict()).get('blueprint',
        'JailHost'))(blueprints, config)

    # 'point' fabric to the jail host
    fab.env['host_string'] = jailhost.ip_addr

    # execute the bootstrap and/or install command
    if arguments['bootstrap']:
        jailhost.bootstrap()
    if arguments['install'] or arguments['bootstrap']:
        jailhost.install()
        exit()

    if arguments['list-blueprints']:
        for name, blueprint in jailhost.available_blueprints.items():
            if arguments['--verbose']:
                description = blueprint.__doc__
            else:
                description = blueprint.__doc__.split('\n')[0]
            print '%s: %s' % (name, description)
        exit()

    if arguments['list-jails']:
        fab.sudo('ezjail-admin list')
        exit()

    # validate the jail name(s)
    jails = arguments['JAIL']
    config_jails = jailhost.jails.keys()
    alljails = set(config_jails).union(set(jailhost.available_blueprints))
    difference = set(jails).difference(alljails)
    if difference:
        print "invalid jail%s %s! (needs to be one of %s)" % \
            (len(difference) > 1 and 's' or '',
                ', '.join(list(difference)),
                ', '.join(list(alljails)))
        exit()

    # execute the jail command
    for jail_name in jails:
        jail = jailhost.jails[jail_name]
        if arguments['init']:
            jail.create()
            jail.prepare()
            jail.update()
        elif arguments['upload']:
            jail.upload()
        elif arguments['update']:
            jail.update()
        elif arguments['prepare']:
            jail.prepare()
        elif arguments['configure']:
            jail.configure()
        elif arguments['destroy']:
            jail.destroy()


if __name__ == '__main__':
    main()
