# flake8: noqa
import os
import tempfile

import logging

from tendrl.commons import flows

LOG = logging.getLogger(__name__)


class SetupSsh(flows.BaseFlow):
    internal = True

    def __init__(self, *args, **kwargs):
        self._defs = {
            "help": "Setup SSH",
            "uuid": "759e639a-1315-11e7-93ae-92361f002672"
        }
        super(SetupSsh, self).__init__(*args, **kwargs)

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
