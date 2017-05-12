from tendrl.commons import objects
from tendrl.commons.utils import cmd_utils


class Cpu(objects.BaseObject):
    def __init__(self, architecture=None, cores_per_socket=None,
                 cpu_family=None, cpu_op_mode=None,
                 model=None, model_name=None, vendor_id=None,
                 *args, **kwargs):
        super(Cpu, self).__init__(*args, **kwargs)
        cpu = self._getNodeCpu()
        self.architecture = architecture or cpu['Architecture']
        self.cores_per_socket = cores_per_socket or cpu["CoresPerSocket"]
        self.cpu_family = cpu_family or cpu["CPUFamily"]
        self.cpu_op_mode = cpu_op_mode or cpu["CpuOpMode"]
        self.model = model or cpu["Model"]
        self.model_name = model_name or cpu["ModelName"]
        self.vendor_id = vendor_id or cpu["VendorId"]
        self.value = 'nodes/{0}/Cpu'

    def _getNodeCpu(self):
        '''returns structure

        {"nodename": [{"Architecture":   "architecture",

                   "CpuOpMode":      "cpuopmode",

                   "CPUs":           "cpus",

                   "VendorId":       "vendorid",

                   "ModelName":      "modelname",

                   "CPUFamily":      "cpufamily",

                   "Model":          "Model",

                   "CoresPerSocket": "corespersocket"}, ...], ...}

        '''
        cmd = cmd_utils.Command("lscpu")
        out, err, rc = cmd.run()
        out = str(out)
        if out:
            info_list = out.split('\n')
            cpuinfo = {
                'Architecture': info_list[0].split(':')[1].strip(),
                'CpuOpMode': info_list[1].split(':')[1].strip(),
                'CPUs': info_list[3].split(':')[1].strip(),
                'VendorId': info_list[9].split(':')[1].strip(),
                'ModelName': info_list[12].split(':')[1].strip(),
                'CPUFamily': info_list[10].split(':')[1].strip(),
                'Model': info_list[11].split(':')[1].strip(),
                'CoresPerSocket': info_list[6].split(':')[1].strip()
            }
        else:
            cpuinfo = {
                'Architecture': '', 'CpuOpMode': '',
                'CPUs': '', 'VendorId': '',
                'ModelName': '', 'CPUFamily': '',
                'Model': '', 'CoresPerSocket': ''
            }

        return cpuinfo


    def render(self):
        self.value = self.value.format(NS.node_context.node_id)
        return super(Cpu, self).render()
