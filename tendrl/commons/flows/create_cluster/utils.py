import json
import uuid

from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.objects.job import Job
from tendrl.commons.utils.ssh import authorize_key
from tendrl.commons.utils import ansible_module_runner

def ceph_create_ssh_setup_jobs(parameters):
    node_list = parameters['Node[]']
    ssh_job_ids = []
    ssh_setup_script = NS.ceph_provisioner.get_plugin().setup()
    if len(node_list) > 1:
        for node in node_list:
            if NS.node_context.node_id != node:
                new_params = parameters.copy()
                new_params['Node[]'] = [node]
                new_params['ssh_setup_script'] = ssh_setup_script
                # create same flow for each node in node list except $this
                payload = {
                    "node_ids": [node],
                    "run": "tendrl.flows.SetupSsh",
                    "status": "new",
                    "parameters": new_params,
                    "parent": parameters['job_id'],
                    "type": "node"
                }
                _job_id = str(uuid.uuid4())
                Job(job_id=_job_id,
                    status="new",
                    payload=json.dumps(payload)).save()
                ssh_job_ids.append(_job_id)
                Event(
                    Message(
                        job_id=parameters['job_id'],
                        flow_id=parameters['flow_id'],
                        priority="info",
                        publisher=NS.publisher_id,
                        payload={"message": "Created SSH setup job %s for node"
                                            " %s" % (_job_id, node)
                                 }
                    )
                )
    return ssh_job_ids

def install_gdeploy():
    # Install gdeploy on the node
    ansible_module_path = "core/packaging/os/yum.py"
    attributes = {}
    attributes["name"] = "gdeploy"
    try:
        runner = ansible_module_runner.AnsibleRunner(
            ansible_module_path,
            **attributes
        )
        runner.run()
    except ansible_module_runner.AnsibleExecutableGenerationFailed:
        raise FlowExecutionFailedError(
            "Failed to install gdeploy"
        )

def install_python_gdeploy():
    attributes = {}
    # Install python-gdeploy on the node
    if NS.config.data['package_source_type'] == 'pip':
        name = "https://github.com/Tendrl/python-gdeploy/archive/master.tar.gz"
        attributes["name"] = name
        attributes["editable"] = "false"
        ansible_module_path = "core/packaging/language/pip.py"
    elif NS.config.data['package_source_type'] == 'rpm':
        name = "tendrl-python-gdeploy"
        ansible_module_path = "core/packaging/os/yum.py"
        attributes["name"] = name
    else:
        raise FlowExecutionFailedError(
            "Failed to install python-gdeploy. Invalid package source type"
        )

    try:
        runner = ansible_module_runner.AnsibleRunner(
            ansible_module_path,
            **attributes
        )
        runner.run()
    except ansible_module_runner.AnsibleExecutableGenerationFailed:
        raise FlowExecutionFailedError(
            "Failed to install python-gdeploy"
        )

def gluster_create_ssh_setup_jobs(parameters):
    node_list = parameters['Node[]']

    ssh_job_ids = []
    ssh_key, err = NS.gluster_provisioner.get_plugin().setup()
    if err != "":
        Event(
            Message(
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
                priority="error",
                publisher=NS.publisher_id,
                payload={"message": "Error generating ssh key"
                         }
            )
        )
        return ssh_job_ids

    ret_val, err = authorize_key.AuthorizeKey(ssh_key).run()
    if ret_val is not True or err != "":
        Event(
            Message(
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
                priority="error",
                publisher=NS.publisher_id,
                payload={
                    "message": "Error adding authorized key"
                }
            )
        )
        return ssh_job_ids

    node_list.remove(NS.node_context.node_id)
    for node in node_list:
        new_params = parameters.copy()
        new_params['Node[]'] = [node]
        new_params['ssh_key'] = ssh_key
        # Create same flow for each node from list except this one
        payload = {
            "node_ids": [node],
            "run": "tendrl.flows.AuthorizeSshKey",
            "status": "new",
            "parameters": new_params,
            "parent": parameters['job_id'],
            "type": "node"
        }
        _job_id = str(uuid.uuid4())
        Job(
            job_id=_job_id,
            status="new",
            payload=json.dumps(payload)
        ).save()
        ssh_job_ids.append(_job_id)
        Event(
            Message(
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Created SSH setup job %s for node %s" %
                                    (_job_id, node)
                         }
            )
        )
    return ssh_job_ids

