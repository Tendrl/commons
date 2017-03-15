# flake8: noqa
import os
import tempfile

import logging

from tendrl.commons import flows

LOG = logging.getLogger(__name__)


class SetupSsh(flows.BaseFlow):
    def run(self):
        ssh_setup_script = self.parameters.get("ssh_setup_script")
        _temp_file = tempfile.NamedTemporaryFile(
            mode="w+",
            prefix="tendrl_provisioner_ssh_",
            suffix="_script",
            dir="/tmp",
            delete=False
        )

        _temp_file.write(ssh_setup_script)
        _temp_file.close()
        os.system("chmod +x %s" % _temp_file.name)
        retval = os.system('/usr/bin/bash %s' % _temp_file.name)
        LOG.info("SSH setup result %s" % retval)
        os.remove(_temp_file.name)

    def load_definition(self):
        return {"help": "Setup SSH",
                "uuid": "dc4c8775-1595-43c7-a6c6-517f0081598f"}
