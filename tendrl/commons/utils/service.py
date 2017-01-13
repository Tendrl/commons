import logging

from ansible_module_runner import AnsibleExecutableGenerationFailed
from ansible_module_runner import AnsibleRunner

ANSIBLE_MODULE_PATH = "core/system/service.py"
LOG = logging.getLogger(__name__)


class Service(object):
    def __init__(self, service_name, exec_path, enabled=None):
        self.attributes = {}
        self.attributes["name"] = service_name
        self.exec_path = exec_path

        if enabled:
            self.attributes["enabled"] = enabled

    def __run_module(self, attr):
        try:
            runner = AnsibleRunner(
                ANSIBLE_MODULE_PATH,
                self.exec_path,
                **attr
            )
            result, err = runner.run()
            LOG.debug("Service Management: %s" % result)
        except AnsibleExecutableGenerationFailed as e:
            LOG.error("Error switching the service: %s to %s state."
                      " Error: %s" % (self.attributes["name"],
                                      attr["state"],
                                      str(e)))
            return e.message, False
        message = result.get("msg", "").encode("ascii")
        state = result.get("state", "").encode("ascii")
        if attr["state"] in ["started", "restarted", "reloaded"]:
            if state == "started":
                success = True
            else:
                success = False
        else:
            if attr["state"] == state:
                success = True
            else:
                success = False
        return message, success

    def start(self):
        attr = self.attributes
        attr.update({"state": "started"})
        return self.__run_module(attr)

    def stop(self):
        attr = self.attributes
        attr.update({"state": "stopped"})
        return self.__run_module(attr)

    def reload(self):
        attr = self.attributes
        attr.update({"state": "reloaded"})
        return self.__run_module(attr)

    def restart(self):
        attr = self.attributes
        attr.update({"state": "restarted"})
        return self.__run_module(attr)
