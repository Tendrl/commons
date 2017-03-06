from tendrl.commons.utils.ansible_module_runner import \
    AnsibleExecutableGenerationFailed
from tendrl.commons.utils.ansible_module_runner import \
    AnsibleRunner
from tendrl.commons.event import Event
from tendrl.commons.message import Message

ANSIBLE_MODULE_PATH = "core/system/authorized_key.py"


class AuthorizeKey(object):
    def __init__(self, ssh_key, user="root"):
        self.attributes = {}
        self.attributes["user"] = user
        # self.attributes["path"] = "/home/%s/.ssh/authorized_keys" % user
        # self.attributes["manage_dir"] = "False"
        self.attributes["key"] = ssh_key

    def run(self):
        try:
            runner = AnsibleRunner(
                ANSIBLE_MODULE_PATH,
                tendrl_ns.config.data[
                    'tendrl_ansible_exec_file'],
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
                    priority="warning",
                    publisher="commons",
                    payload={"message": "Copying authorize key failed %s. "
                             "Error: %s" % (
                                 self.attributes["_raw_params"], str(e.message))}
                )
            )
        if err is not "":
            Event(
                Message(
                    priority="warning",
                    publisher="commons",
                    payload={"message": "Unable to copy authorize key .err:%s" % err}
                )
            )
            return False
        else:
            return True
