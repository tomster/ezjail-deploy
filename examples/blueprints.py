from fabric import api as fab
from ezjaildeploy.api import JailHost, BaseJail


class CryptoJailHost(JailHost):

    """ Installs and configures ezjail to use an encrypted ZFS pool.
    """

    iface = 'em0'
    root_device = 'ada0'
    zpool = 'jails'

    def bootstrap(self):
        super(CryptoJailHost, self).bootstrap()

        # configure IP addresses for the jails
        fab.sudo("""echo 'cloned_interfaces="lo1"' >> /etc.rc.conf""")
        fab.sudo("""echo 'ipv4_addrs_lo1="127.0.0.2-10/32"' >> /etc.rc.conf""")
        fab.sudo('ifconfig lo1 create')
        for ip in range(2, 11):
            fab.sudo('ifconfig lo1 alias 127.0.0.%s' % ip)

        # set up NAT for the jails
        fab.sudo("""echo 'nat on %s from 127.0/24 to any -> %s' > /etc/pf.conf""" % (self.iface, self.ip_addr))
        fab.sudo("""echo 'pf_enable="YES"' >> /etc/rc.conf""")
        fab.sudo("""/etc/rc.d/pf start""")

        # configure crypto volume for jails
        fab.sudo("""gpart add -t freebsd-zfs -l jails -a8 %s""" % self.root_device)
        fab.puts("You will need to enter the passphrase for the crypto volume THREE times")
        fab.puts("Once to provide it for encrypting, a second time to confirm it and a third time to mount the volume")
        fab.sudo("""geli init gpt/jails""")
        fab.sudo("""geli attach gpt/jails""")
        fab.sudo("""zpool create jails gpt/jails.eli""")
        fab.sudo("""sudo zfs mount -a""")  # sometimes the newly created pool is not mounted automatically


class UnboundJail(BaseJail):

    """ Configures a simply forwarding, caching nameserver.
    """

    ports_to_install = ['dns/unbound']
