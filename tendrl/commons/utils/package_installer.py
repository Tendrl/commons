from ansible_module_runner import AnsibleExecutableGenerationFailed
from ansible_module_runner import AnsibleRunner

from tendrl.commons.event import Event
from tendrl.commons.message import Message


class Installer(object):
    def __init__(self, package_name, package_type, package_version=None):
        self.attributes = {}
        self.attributes["name"] = package_name

        if package_type == "pip":
            self.attributes["editable"] = "false"
            self.ansible_module_path = "core/packaging/language/pip.py"
        elif package_type == "rpm":
            self.ansible_module_path = "core/packaging/os/yum.py"
        elif package_type == "deb":
            self.ansible_module_path = "core/packaging/os/apt.py"
        else:
            Event(
                Message(
                    priority="error",
                    publisher=tendrl_ns.publisher_id,
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
            runner = AnsibleRunner(
                self.ansible_module_path,
                **self.attributes
            )
            result, err = runner.run()
            Event(
                Message(
                    priority="debug",
                    publisher=tendrl_ns.publisher_id,
                    payload={"message": "INSTALLATION: %s" % result}
                )
            )
        except AnsibleExecutableGenerationFailed as e:
            Event(
                Message(
                    priority="error",
                    publisher=tendrl_ns.publisher_id,
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
