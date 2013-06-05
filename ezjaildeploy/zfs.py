from fabric import api as fab
from datetime import datetime


def snapshot(host, name, jail=None):
    """ create a ZFS snapshot of the given jail, or, if None given from the jailhost.

    The name of the snapshot will have an iso format timestamp appended."""

    if host.jailzfs is None:
        return

    if jail is None:
        zfs_fs = host.jailzfs
    else:
        zfs_fs = '%s/%s' % (host.jailzfs, jail)

    snapshot_name = '%s@%s-%s' % (zfs_fs, datetime.now().isoformat(), name)
    fab.sudo("""zfs snapshot %s""" % snapshot_name)
