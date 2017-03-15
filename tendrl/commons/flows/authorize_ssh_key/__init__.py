import logging

from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.utils.ssh import authorize_key

LOG = logging.getLogger(__name__)


class AuthorizeSshKey(flows.BaseFlow):
    def run(self):
        ssh_key = self.parameters['ssh_key']
        ret_val, err = authorize_key.AuthorizeKey(ssh_key).run()
        if ret_val is not True or err != "":
            raise FlowExecutionFailedError(err)
        return True

    def load_definition(self):
        return {
            "help": "Authorize ssh key",
            "uuid": "dc4c8775-1595-43c7-a6c6-517f0081599f"
        }
