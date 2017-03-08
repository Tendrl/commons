import psutil
from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.utils import cmd_utils


def find_status():
    """This util is used to find the status of

    sshd service. It will identify sshd status using
    process id of sshd service.

    input:
        (No input required)

    output:
        {"name": "",
         "port": "",
         "status": ""}
    """

    sshd = {"name": "",
            "port": "",
            "status": ""}
    cmd = cmd_utils.Command("systemctl show sshd.service")
    out, err, rc = cmd.run(NS.config.data[
                           'tendrl_ansible_exec_file'])
    if not err:
        pid = _find_pid(out)
        if pid != 0:
            p = psutil.Process(pid)
            result = [con for con in p.connections() if con.status ==
                  psutil.CONN_LISTEN and con.laddr[0] == "0.0.0.0"]
            if result != []:
                sshd["name"] = p.name()
                sshd["port"] = int(result[0].laddr[1])
                sshd["status"] = result[0].status
            else:
                err = "Unable to find port number"
                Event(
                    Message(
                        priority="warning",
                        publisher="commons",
                        payload={"message": err}
                    )
                )
        else:
            err = "sshd service is not running" 
            Event(
                Message(
                    priority="warning",
                    publisher="commons",
                    payload={"message": err}
                )
            )

    else:
        Event(
            Message(
                priority="warning",
                publisher="commons",
                payload={"message": err}
            )
        )
    return sshd, err

def _find_pid(out):
    pid = 0 # 0 when sshd not run
    out = out.split("\n")
    for item in out:
        item = item.split("=")
        if "MainPID" == item[0]:
            pid = int(item[1])
    return pid
