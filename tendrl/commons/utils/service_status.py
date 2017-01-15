from tendrl.commons.utils import command as cmd_util


class ServiceStatus(object):
    """systemd services provider."""

    def __init__(self, name):
        self.name = name

    def _execute_service_command(self, argument):
        service_cmd = "systemctl "
        service_cmd += " ".join(argument) if isinstance(
            argument, tuple) else argument
        service_cmd += " %s.service" % self.name
        command = cmd_util.Command(service_cmd)
        return command.run()

    def exists(self):
        stdout, stderr, rc = self._execute_service_command(
            (
                'show',
                '-p',
                'LoadState',
            )
        )
        if rc == 0 and stdout.find('LoadState=loaded') >= 0:
            return True
        else:
            return False

    def status(self):
        stdout, stderr, rc = self._execute_service_command('status')
        if stdout and rc == 0:
            return True
        else:
            return False
