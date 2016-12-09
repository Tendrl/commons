from ansible_module_runner import AnsibleExecutableGenerationFailed
from ansible_module_runner import AnsibleRunner
import logging

ANSIBLE_MODULE_PATH = "core/commands/command.py"
LOG = logging.getLogger(__name__)


class Command(object):
    def __init__(self, command):
        self.attributes = {"_raw_params": command}

    def run(self):
        try:
            runner = AnsibleRunner(
                ANSIBLE_MODULE_PATH,
                **self.attributes
            )
            result, err = runner.run()
        except AnsibleExecutableGenerationFailed as e:
            LOG.error("could not run the command %s. Error: %s" % (
                self.attributes["_raw_params"], str(e)))
            return {}, e.message
        return result, err
