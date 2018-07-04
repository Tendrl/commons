import copy
import uuid

from etcd import EtcdKeyNotFound

from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils import log_utils as logger
from tendrl.commons.utils.ssh import authorize_key


def install_gdeploy():
    # Install gdeploy on the node
    ansible_module_path = "packaging/os/yum.py"
    attributes = dict()
    attributes["name"] = "gdeploy"
    try:
        runner = ansible_module_runner.AnsibleRunner(
            ansible_module_path,
            **attributes
        )
    except ansible_module_runner.AnsibleModuleNotFound:
        # Backward compat ansible<=2.2
        runner = ansible_module_runner.AnsibleRunner(
            "core/" + ansible_module_path,
            **attributes
        )
    try:
        result, err = runner.run()
        if result.get('failed', None):
            raise FlowExecutionFailedError(
                "Failed to install gdeploy. %s" % result['msg']
            )
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
        ansible_module_path = "packaging/language/pip.py"
    elif NS.config.data['package_source_type'] == 'rpm':
        name = "python-gdeploy"
        ansible_module_path = "packaging/os/yum.py"
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
    except ansible_module_runner.AnsibleModuleNotFound:
        # Backward compat ansible<=2.2
        runner = ansible_module_runner.AnsibleRunner(
            "core/" + ansible_module_path,
            **attributes
        )
    try:
        result, err = runner.run()
        if result.get('failed', None):
            raise FlowExecutionFailedError(
                "Failed to install python-gdeploy. %s" % result['msg']
            )
    except ansible_module_runner.AnsibleExecutableGenerationFailed:
        raise FlowExecutionFailedError(
            "Failed to install python-gdeploy"
        )


def gluster_create_ssh_setup_jobs(parameters, skip_current_node=False):
    node_list = copy.deepcopy(parameters['Node[]'])

    ssh_job_ids = []
    ssh_key, err = NS.gluster_provisioner.get_plugin().setup()
    if err != "":
        _msg = "Error generating ssh key on node %s" % NS.node_context.node_id
        logger.log(
            "error",
            NS.publisher_id,
            {"message": _msg},
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id']
        )
        raise FlowExecutionFailedError(_msg)

    if not skip_current_node:
        ret_val, err = authorize_key.AuthorizeKey(ssh_key).run()
        if ret_val is not True or err != "":
            _msg = "Error adding authorized key for node %s" % \
                   NS.node_context.node_id
            logger.log(
                "error",
                NS.publisher_id,
                {"message": _msg},
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id']
            )
            raise FlowExecutionFailedError(_msg)
        node_list.remove(NS.node_context.node_id)

    for node in node_list:
        if node == NS.node_context.node_id:
            continue
        new_params = parameters.copy()
        new_params['Node[]'] = [node]
        new_params['ssh_key'] = ssh_key
        # Create same flow for each node from list except this one
        payload = {
            "tags": ["tendrl/node_%s" % node],
            "run": "tendrl.flows.AuthorizeSshKey",
            "status": "new",
            "parameters": new_params,
            "parent": parameters['job_id'],
            "type": "node"
        }
        _job_id = str(uuid.uuid4())
        NS.tendrl.objects.Job(
            job_id=_job_id,
            status="new",
            payload=payload
        ).save()
        ssh_job_ids.append(_job_id)
        logger.log(
            "info",
            NS.publisher_id,
            {"message": "Created SSH setup job(jobID: %s) for %s" %
                        (_job_id, node)},
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id']
        )
    return ssh_job_ids


def acquire_node_lock(parameters):
    # check node_id is present
    for node in parameters['Node[]']:
        if not NS.tendrl.objects.NodeContext(
            node_id=node
        ).exists():
            raise FlowExecutionFailedError(
                "Unknown Node %s, cannot lock" %
                node)
    # check job is parent or child
    job = NS.tendrl.objects.Job(
        job_id=parameters['job_id']
    ).load()
    p_job_id = None
    if "parent" in job.payload:
        p_job_id = job.payload['parent']

    for node_id in parameters['Node[]']:
        nc = NS.tendrl.objects.NodeContext(node_id=node_id).load()
        try:
            lock_owner_job = nc.locked_by
            # If the parent job has aquired lock on participating nodes,
            # dont you worry child job :)
            if p_job_id is not None and lock_owner_job is not None:
                if p_job_id == lock_owner_job:
                    continue
                else:
                    raise FlowExecutionFailedError(
                        "Cannot proceed further, "
                        "Node (%s) is already locked "
                        "by Job (%s)" % (
                            node_id,
                            lock_owner_job
                        )
                    )
        except EtcdKeyNotFound:
            # To check what are all the nodes are already locked
            continue

    for node_id in parameters['Node[]']:
        nc = NS.tendrl.objects.NodeContext(node_id=node_id).load()
        lock_owner_job = nc.locked_by
        if p_job_id is not None and lock_owner_job is not None and \
            p_job_id == lock_owner_job:
            continue
        else:
            lock_owner_job = str(parameters["job_id"])
            nc.locked_by = lock_owner_job
            nc.save()
            logger.log(
                "info",
                NS.publisher_id,
                {"message": "Acquired lock (%s) on (%s)" % (
                    lock_owner_job, node_id)},
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id']
            )


def release_node_lock(parameters):
    for node_id in parameters['Node[]']:
        nc = NS.tendrl.objects.NodeContext(node_id=node_id).load()
        try:
            lock_owner_job = nc.locked_by
            if lock_owner_job == parameters['job_id']:
                nc.locked_by = None
                nc.save()
                logger.log(
                    "info",
                    NS.publisher_id,
                    {"message": "Released lock (%s) on (%s)" %
                                (lock_owner_job, node_id)},
                    job_id=parameters['job_id'],
                    flow_id=parameters['flow_id']
                )
        except EtcdKeyNotFound:
            continue
