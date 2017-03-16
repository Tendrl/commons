from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.utils.ansible_module_runner import \
    AnsibleExecutableGenerationFailed
from tendrl.commons.utils.ansible_module_runner import \
    AnsibleRunner

ANSIBLE_MODULE_PATH = "core/system/authorized_key.py"


class AuthorizeKey(object):
    """AuthorizeKey class is used to copy the given ssh-key

    to particular user. A default user is root.
    Here ssh_key is mandatory and user is optional.
    At the time of initalize it will take user and ssh-key as
    parameter.

    input:
        ssh_key
        user(optional)

    output:
        True/False, None/error
    """
    def __init__(self, ssh_key, user="root"):
        self.attributes = {}
        self.attributes["user"] = user
        self.attributes["key"] = ssh_key

    def run(self):
        """This function is used to copy the given authorize ssh-key

        output:
            True/False, error
        """
        try:
            runner = AnsibleRunner(
                ANSIBLE_MODULE_PATH,
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
                             "Error: %s" % (self.attributes["_raw_params"],
                                            str(e.message))}
                )
            )
        if err is not "":
            Event(
                Message(
                    priority="warning",
                    publisher="commons",
                    payload={"message": "Unable to copy authorize key "
                                        ".err:%s" % err}
                )
            )
            return False, err
        else:
            return True, err
