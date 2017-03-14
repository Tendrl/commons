import logging
import os
import subprocess
import tempfile

import ansible.executor.module_common as module_common
from ansible import modules

LOG = logging.getLogger(__name__)

try:
    import json
except ImportError:
    import simplejson as json


class AnsibleExecutableGenerationFailed(Exception):
    def __init__(self, module_path=None, arguments=None, err=None):
        self.message = "Executabe could not be generated for module" \
                       " %s . Error: %s" % (
                           str(module_path), str(err))


class AnsibleRunner(object):
    """Class that can be used to run ansible modules

    """

    def __init__(self, module_path, **kwargs):
        self.module_path = modules.__path__[0] + "/" + module_path
        if not os.path.isfile(self.module_path):
            LOG.error("Module path: %s does not exist" % self.module_path)
            raise ValueError
        if kwargs == {}:
            LOG.error("Empty argument dictionary")
            raise ValueError
        else:
            self.argument_dict = kwargs

    def __generate_executable_module(self):
        modname = os.path.basename(self.module_path)
        modname = os.path.splitext(modname)[0]
        try:
            (module_data, module_style, shebang) = \
                module_common.modify_module(
                    modname,
                    self.module_path,
                    self.argument_dict,
                    task_vars={}
                )
        except Exception as e:
            LOG.error("Could not generate executable data for module"
                      ": %s. Error: %s" % (self.module_path, str(e)))
            raise AnsibleExecutableGenerationFailed(
                self.module_path,
                str(e)
            )
        return module_data

    def run(self):
        module_data = self.__generate_executable_module()
        _temp_file = tempfile.NamedTemporaryFile(mode="w+",
                                                 prefix="tendrl_ansible_",
                                                 suffix="exec",
                                                 dir="/tmp",
                                                 delete=False)

        _temp_file.write(module_data)
        _temp_file.close()

        try:
            os.system("chmod +x %s" % _temp_file.name)
            cmd = subprocess.Popen(
            _temp_file.name,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
            out, err = cmd.communicate()
            result = json.loads(out)

        except (subprocess.CalledProcessError, ValueError) as ex:
            result = repr(ex)
            err = result
        finally:
            os.remove(_temp_file.name)

        return result, err
