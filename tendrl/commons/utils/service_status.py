from tendrl.commons.utils import cmd_utls


class ServiceStatus(object):
    """systemd services provider."""

    def __init__(self, name, exec_path):
        self.name = name
        self.exec_path = exec_path

    def _execute_service_command(self, argument):
        service_cmd = "systemctl "
        service_cmd += " ".join(argument) if isinstance(
            argument, tuple) else argument
        service_cmd += " %s.service" % self.name
        command = cmd_utls.Command(service_cmd)
        return command.run(self.exec_path)

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
