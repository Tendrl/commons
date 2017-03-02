import psutil
from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.utils import cmd_utils


def sshd_status():
    cmd = cmd_utils.Command("systemctl show sshd.service")
    out, err, rc = cmd.run(tendrl_ns.config.data[
                           'tendrl_ansible_exec_file'])
    if not err:
        sshd = {}
        out = out.split("\n")
        pid = find_pid(out)
        if pid == 0:
            Event(
                Message(
                    priority="error",
                    publisher="commons",
                    payload={"message": "sshd service is not run"}
                )
            )
            return sshd, "sshd service is not run"

        p = psutil.Process(pid)

        ''' p.connections() will give result like

        [pconn(fd=3, family=10, type=1, laddr=('0.0.0.0', 22),
        raddr=('::1', 54960), status='LISTEN')]
        '''
        result = [con for con in p.connections() if con.status ==
                  psutil.CONN_LISTEN and con.laddr[0] == "0.0.0.0"]
        if result == []:
            Event(
                Message(
                    priority="error",
                    publisher="commons",
                    payload={"message": "Unable to find port number"}
                )
            )
            return sshd, "Unable to find port number"

        sshd["name"] = p.name()
        sshd["port"] = int(result[0].laddr[1])
        sshd["status"] = result[0].status
        return sshd, None
    else:
        Event(
            Message(
                priority="error",
                publisher="commons",
                payload={"message": err}
            )
        )
        return None, err

def find_pid(out):
    pid = 0 # 0 when sshd not run
    for item in out:
        item = item.split("=")
        if "MainPID" == item[0]:
            pid = int(item[1])
    return pid
