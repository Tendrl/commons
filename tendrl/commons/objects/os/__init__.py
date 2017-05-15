import platform
import socket


from tendrl.commons.utils import cmd_utils

from tendrl.commons import objects


class Os(objects.BaseObject):
    def __init__(self, kernel_version=None, os=None,
                 os_version=None, selinux_mode=None,
                 *args, **kwargs):
        super(Os, self).__init__(*args, **kwargs)
        os_details = self._getNodeOs()
        self.kernel_version = kernel_version or os_details["KernelVersion"]
        self.os = os or os_details["Name"]
        self.os_version = os_version or os_details["OSVersion"]
        self.selinux_mode = selinux_mode or os_details["SELinuxMode"]
        self.value = 'nodes/{0}/Os'

    def _getNodeOs(self):
        cmd = cmd_utils.Command("getenforce")
        out, err, rc = cmd.run()
        se_out = str(out)

        os_out = platform.linux_distribution()

        osinfo = {
            'Name': os_out[0],
            'OSVersion': os_out[1],
            'KernelVersion': platform.release(),
            'SELinuxMode': se_out,
            'FQDN': socket.getfqdn()
        }

        return osinfo

    def render(self):
        self.value = self.value.format(NS.node_context.node_id)
        return super(Os, self).render()
