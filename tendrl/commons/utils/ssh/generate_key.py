from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.utils import ansible_module_runner


ANSIBLE_MODULE_PATH = "system/user.py"


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
            runner = ansible_module_runner.AnsibleRunner(
                ANSIBLE_MODULE_PATH,
                **self.attributes
            )
        except ansible_module_runner.AnsibleModuleNotFound:
            # Backward compat ansible<=2.2
            runner = ansible_module_runner.AnsibleRunner(
                "core/" + ANSIBLE_MODULE_PATH,
                **self.attributes
            )
        try:
            out, err = runner.run()
            Event(
                Message(
                    priority="debug",
                    publisher="commons",
                    payload={"message": "SSH-key Generation: %s" % out}
                )
            )
        except ansible_module_runner.AnsibleExecutableGenerationFailed as e:
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
                    payload={"message": "Unable to generate ssh-key .err: "
                                        "%s" % err}
                )
            )
        elif "ssh_public_key" in out:
            result = out["ssh_public_key"]

        return result, err
