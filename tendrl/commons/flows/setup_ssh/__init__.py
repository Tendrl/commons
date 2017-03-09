# flake8: noqa
import os
import tempfile

from tendrl.commons import flows


class SetupSsh(flows.BaseFlow):
    def run(self):
        ssh_setup_script = self.parameters.get("ssh_setup_script")
        _temp_file = tempfile.NamedTemporaryFile(mode="w+",
                                                 prefix="tendrl_ceph_provisioner_ssh_",
                                                 suffix="_script",
                                                 dir="/tmp",
                                                 delete=False)

        _temp_file.write(ssh_setup_script)
        _temp_file.close()
        ret_val = os.system('/usr/bin/bash %s' % _temp_file.name)
        if ret_val == 0:
            return True
        else:
            return False

    def load_definition(self):
        return {"help": "Setup SSH",
                "uuid": "dc4c8775-1595-43c7-a6c6-517f0081598f"}