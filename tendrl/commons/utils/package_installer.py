from tendrl.commons.utils import ansible_module_runner

from tendrl.commons.event import Event
from tendrl.commons.message import Message


class Installer(object):
    def __init__(self, package_name, package_type, package_version=None):
        self.attributes = dict()
        self.attributes["name"] = package_name

        if package_type == "pip":
            self.attributes["editable"] = "false"
            self.ansible_module_path = "packaging/language/pip.py"
        elif package_type == "rpm":
            self.ansible_module_path = "packaging/os/yum.py"
        elif package_type == "deb":
            self.ansible_module_path = "packaging/os/apt.py"
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={"message": "Unsupported package type: %s" %
                                        package_type
                             }
                )
            )
            raise ValueError("Unsupported package type: %s" % package_type)

        if package_version:
            self.attributes["name"] = package_name + "-" + package_version

    def install(self):
        try:
            runner = ansible_module_runner.AnsibleRunner(
                self.ansible_module_path,
                **self.attributes
            )
        except ansible_module_runner.AnsibleModuleNotFound:
            # Backward compat ansible<=2.2
            self.ansible_module_path = "core/" + self.ansible_module_path
            runner = ansible_module_runner.AnsibleRunner(
                self.ansible_module_path,
                **self.attributes
            )

        try:
            result, err = runner.run()
            Event(
                Message(
                    priority="debug",
                    publisher=NS.publisher_id,
                    payload={"message": "INSTALLATION: %s" % result}
                )
            )
        except ansible_module_runner.AnsibleExecutableGenerationFailed as e:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={"message": "Could not install package: %s. Error:"
                                        " %s" %
                                        (self.attributes["name"], str(e))
                             }
                )
            )
            return e.message, False
        message = result.get("msg", "").encode("ascii")
        if result.get("rc", -1) == 0:
            success = True
        else:
            success = False
        return message, success
