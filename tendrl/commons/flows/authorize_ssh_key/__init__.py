import logging

from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.utils.ssh import authorize_key

LOG = logging.getLogger(__name__)


class AuthorizeSshKey(flows.BaseFlow):
    internal = True
    
    def __init__(self, *args, **kwargs):
        self._defs = {}
        super(AuthorizeSshKey, self).__init__(*args, **kwargs)
        
    def run(self):
        ssh_key = self.parameters['ssh_key']
        ret_val, err = authorize_key.AuthorizeKey(ssh_key).run()
        if ret_val is not True or err != "":
            raise FlowExecutionFailedError(err)
        return True
