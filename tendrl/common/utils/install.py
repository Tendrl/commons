from ansible_module_runner import AnsibleExecutableGenerationFailed
from ansible_module_runner import AnsibleRunner
import logging

LOG = logging.getLogger(__name__)


class Installer(object):
    def __init__(self, package_name, package_type, package_version=None):
        self.attributes = {}
        self.attributes["name"] = package_name

        if package_type == "pip":
            self.attributes["editable"] = "false"
            self.ansible_module_path = "core/packaging/language/pip.py"
        elif package_type == "yum":
            self.ansible_module_path = "core/packaging/os/yum.py"
        elif package_type == "deb":
            self.ansible_module_path = "core/packaging/os/apt.py"
        else:
            LOG.error("Unsupported package type: %s" % package_type)
            raise ValueError("Unsupported package type: %s" % package_type)

        if package_version:
            self.attributes["version"] = package_version

    def install(self):
        try:
            runner = AnsibleRunner(
                self.ansible_module_path,
                **self.attributes
            )
            result, err = runner.run()
        except AnsibleExecutableGenerationFailed as e:
            LOG.error("Could not install package: %s."
                      " Error: %s" % (self.attributes["name"], str(e)))
            return {}, e.message
        return result, err
