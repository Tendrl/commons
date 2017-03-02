from ansible_module_runner import AnsibleExecutableGenerationFailed
from ansible_module_runner import AnsibleRunner
from tendrl.commons.event import Event
from tendrl.commons.message import Message

ANSIBLE_MODULE_PATH = "core/system/authorized_key.py"


class AuthorizeKey(object):
    def __init__(self, ssh_key, user="root"):
        self.attributes = {}
        self.attributes["user"] = user
        self.attributes["state"] = "present"
        self.attributes["key"] = ssh_key

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
                    payload={"message": "Authorize key: %s" % result}
                )
            )
        except AnsibleExecutableGenerationFailed as e:
            Event(
                Message(
                    priority="error",
                    publisher="commons",
                    payload={"message": "Copying authorize key failed %s. "
                             "Error: %s" % (
                                 self.attributes["_raw_params"], str(e))}
                )
            )
            return False, str(e.message)
        # if key is copied success fully then result should be None
        if result is not None:
            # result not None so some err came
            return False, result
        else:
            return True, None
