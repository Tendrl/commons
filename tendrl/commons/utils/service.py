from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils import log_utils as logger

ANSIBLE_MODULE_PATH = "system/service.py"


class Service(object):
    def __init__(
        self,
        service_name,
        publisher_id=None,
        node_id=None,
        enabled=None
    ):
        self.attributes = {}
        self.attributes["name"] = service_name
        self.publisher_id = publisher_id
        if not publisher_id:
            self.publisher_id = NS.publisher_id
        self.node_id = node_id
        if not node_id:
            self.node_id = NS.node_context.node_id
        if enabled:
            self.attributes["enabled"] = enabled

    def __run_module(self, attr):
        try:
            runner = ansible_module_runner.AnsibleRunner(
                ANSIBLE_MODULE_PATH,
                publisher_id=self.publisher_id,
                node_id=self.node_id,
                **attr
            )
        except ansible_module_runner.AnsibleModuleNotFound:
            # Backward compat ansible<=2.2
            runner = ansible_module_runner.AnsibleRunner(
                "core/" + ANSIBLE_MODULE_PATH,
                publisher_id=self.publisher_id,
                node_id=self.node_id,
                **attr
            )
        try:
            result, err = runner.run()
            logger.log(
                "debug",
                self.publisher_id,
                {"message": "Service Management: %s" % result}
            )
        except ansible_module_runner.AnsibleExecutableGenerationFailed as e:
            logger.log(
                "error",
                self.publisher_id,
                {"message": "Error switching the service: "
                            "%s to %s state. Error: %s" %
                            (self.attributes["name"],
                             attr["state"],
                             str(e)
                             )},
                node_id=self.node_id
            )
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
