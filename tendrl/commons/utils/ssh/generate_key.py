from tendrl.commons.utils.ansible_module_runner import \
    AnsibleExecutableGenerationFailed
from tendrl.commons.utils.ansible_module_runner import \
    AnsibleRunner
from tendrl.commons.event import Event
from tendrl.commons.message import Message

ANSIBLE_MODULE_PATH = "core/system/user.py"


class GenerateKey(object):
    """GenerateKey is used to generate ssh-key

    for the user. If the user is not exist then
    it will create user with ssh-key.

    At the time of initialize it takes user and
    group as parameters.
    
    input:
        user (default is root)
        group (optional)

    output:
        "some ssh-key", error/None
    """
    def __init__(self, user="root", group=None):
        self.attributes = {}
        self.attributes["name"] = user
        self.attributes["generate_ssh_key"] = "yes"
        self.attributes["ssh_key_bits"] = 2048
        if group is not None:
            self.attributes["group"] = group

    def run(self):
        result = None
        try:
            runner = AnsibleRunner(
                ANSIBLE_MODULE_PATH,
                NS.config.data[
                    'tendrl_ansible_exec_file'],
                **self.attributes
            )
            out, err = runner.run()
            Event(
                Message(
                    priority="debug",
                    publisher="commons",
                    payload={"message": "SSH-key Generation: %s" % out}
                )
            )
        except AnsibleExecutableGenerationFailed as e:
            err = str(e.message)
            Event(
                Message(
                    priority="warning",
                    publisher="commons",
                    payload={"message": "SSH-Key Genertion failed %s. "
                             "Error: %s" % (
                                 self.attributes["_raw_params"], err)}
                )
            )
        if out is not None and "ssh_public_key" not in out:
            err = out
            Event(
                Message(
                    priority="warning",
                    publisher="commons",
                    payload={"message":"Unable to generate ssh-key .err: %s" % err}
                )
            )
        elif "ssh_public_key" in out:
            result = out["ssh_public_key"]

        return result, err
