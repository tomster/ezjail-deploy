from fabric import api as fab
from ezjaildeploy import api


@api.uplod_files([
    'var/db/ports/options',
    '/usr/local/etc/'])
@api.user_data([  # or use *args
    '/usr/local/etc/foo.conf',
    '/opt/local/briefkasten/var',
    '/opt/local/briefkasten/etc',
    '/usr/local/etc/sshd/config'])
@api.install_packages([
    'lang/python',
    'lib/jpeg'])
class BriefkastenInstallWebAppStage(api.BaseStage):

    create_user = api.steps.CreateUser(
        name='briefkasten',
        groups='www')

    upload_git = api.steps.UploadGitRepo(
        branch='testing',
        local_path='src/briefkasten',
        remote_path='/opt/local/')

    mkdir = api.steps.Sudo('mkdir ', user='briefkasten')

    @api.uplod_files([
        '/opt/hosting/buildout.cfg'])
    @api.step
    def run_buildout(self):
        with fab.cd(self.foo_dir):
            fab.sudo('sfsdfsdfs')
            self.console('sdfsdfds')
            if api.exists(self.foo):
                self.console('sdfdsfds')

    @api.step
    def install_startup_script(self):
        self.console('fooo')
        self.host.stages.webserver.listen_port


class BriefkastenStartWebAppStage(api.BaseStage):

    @api.step
    def start_supervisord(self):
        self.console('bin/supervisord')


class BriefkastenHost(api.JailHost):

    webserver = BriefkastenStartWebAppStage()
