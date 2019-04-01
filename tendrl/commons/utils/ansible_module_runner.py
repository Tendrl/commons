import os
import subprocess
import tempfile

import ansible.executor.module_common as module_common
from ansible import modules

from tendrl.commons.utils import log_utils as logger

try:
    import json
except ImportError:
    import simplejson as json


class AnsibleExecutableGenerationFailed(Exception):
    def __init__(self, module_path=None, arguments=None, err=None):
        self.message = "Executabe could not be generated for module" \
                       " %s . Error: %s" % (
                           str(module_path), str(err))


class AnsibleModuleNotFound(Exception):
    def __init__(self, module_path=None):
        self.message = "Ansible module %s not found" % str(module_path)


class AnsibleRunner(object):
    """Class that can be used to run ansible modules

    """

    def __init__(
        self,
        module_path,
        publisher_id=None,
        node_id=None,
        **kwargs
    ):
        self.module_path = modules.__path__[0] + "/" + module_path
        self.publisher_id = publisher_id or NS.publisher_id
        self.node_id = node_id or NS.node_context.node_id
        if not os.path.isfile(self.module_path):
            logger.log(
                "debug",
                self.publisher_id,
                {"message": "Module path: %s does not exist" %
                    self.module_path},
                node_id=self.node_id
            )
            raise AnsibleModuleNotFound(module_path=self.module_path)
        if kwargs == {}:
            logger.log(
                "debug",
                self.publisher_id,
                {"message": "Empty argument dictionary"},
                node_id=self.node_id
            )
            raise ValueError
        else:
            self.argument_dict = kwargs
            self.argument_dict['_ansible_selinux_special_fs'] = \
                ['nfs', 'vboxsf', 'fuse', 'ramfs']

    def __generate_executable_module(self):
        modname = os.path.basename(self.module_path)
        modname = os.path.splitext(modname)[0]
        try:
            (module_data, module_style, shebang) = \
                module_common.modify_module(
                    modname,
                    self.module_path,
                    self.argument_dict,
                    None,
                    task_vars={}
                )
        except Exception as e:
            logger.log(
                "debug",
                self.publisher_id,
                {"message": "Could not generate ansible "
                            "executable data "
                            "for module  : %s. Error: %s" %
                            (self.module_path, str(e))},
                node_id=self.node_id
            )
            raise AnsibleExecutableGenerationFailed(
                module_path=self.module_path,
                err=str(e)
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
            cmd = subprocess.Popen(_temp_file.name, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE
                                   )
            out, err = cmd.communicate()
            if err:
                result = {'stderr': repr(err)}
            else:
                result = json.loads(out)

        except (subprocess.CalledProcessError, ValueError) as ex:
            result = {'stderr': repr(ex)}
            err = repr(ex)
        finally:
            os.remove(_temp_file.name)
        return result, err
