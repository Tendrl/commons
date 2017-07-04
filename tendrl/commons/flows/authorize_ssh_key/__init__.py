from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.utils.ssh import authorize_key


class AuthorizeSshKey(flows.BaseFlow):
    internal = True

    def __init__(self, *args, **kwargs):
        self._defs = {
            "help": "Authorize SSH Key",
            "uuid": "759e639a-1315-11e7-93ae-92361f002671"
        }
        super(AuthorizeSshKey, self).__init__(*args, **kwargs)

    def run(self):
        ssh_key = self.parameters['ssh_key']
        ret_val, err = authorize_key.AuthorizeKey(ssh_key).run()
        if ret_val is not True or err != "":
            raise FlowExecutionFailedError(err)
        return True
