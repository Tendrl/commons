from ansible_module_runner import AnsibleExecutableGenerationFailed
from ansible_module_runner import AnsibleRunner
from tendrl.commons.event import Event
from tendrl.commons.message import Message

ANSIBLE_MODULE_PATH = "core/system/user.py"


class GenerateSSH(object):
    def __init__(self, user="root", group=None):
        self.attributes = {}
        self.attributes["name"] = user
        self.attributes["generate_ssh_key"] = "yes"
        self.attributes["ssh_key_bits"] = 2048
        if group is not None:
            self.attributes["group"] = group

    def run(self, exec_path):
        try:
            runner = AnsibleRunner(
                ANSIBLE_MODULE_PATH,
                exec_path,
                **self.attributes
            )
            result, err = runner.run()
            Event(
                Message(
                    priority="debug",
                    publisher="commons",
                    payload={"message": "SSH-key Generation: %s" % result}
                )
            )
        except AnsibleExecutableGenerationFailed as e:
            Event(
                Message(
                    priority="error",
                    publisher="commons",
                    payload={"message": "SSH-Key Genertion failed %s. "
                             "Error: %s" % (
                                 self.attributes["_raw_params"], str(e))}
                )
            )
            return None, str(e.message)
        if "ssh_public_key" in result:
            return result["ssh_public_key"], None
        else:
            return None, result
