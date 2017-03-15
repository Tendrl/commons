import subprocess
from tendrl.commons import objects


class Cmd(objects.BaseObject):
    def run(self):
        cmd = self.parameters.get("Node.cmd_str")
        cmd = ["nohup"] + cmd.split(" ")
        subprocess.Popen(cmd)
        return True
