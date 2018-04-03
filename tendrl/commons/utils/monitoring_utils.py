import uuid


def update_dashboard(res_name, res_type, integration_id, action):
    _job_id = str(uuid.uuid4())
    _params = {
        "TendrlContext.integration_id": NS.tendrl_context.integration_id,
        "TendrlContext.cluster_name": NS.tendrl_context.cluster_name,
        "Trigger.resource_name": res_name,
        "Trigger.resource_type": res_type,
        "Trigger.action": action
    }
    _job_payload = {
        "tags": ["tendrl/integration/monitoring"],
        "run": "monitoring.flows.UpdateDashboard",
        "status": "new",
        "parameters": _params,
        "type": "monitoring"
    }
    NS.tendrl.objects.Job(
        job_id=_job_id,
        status="new",
        payload=_job_payload
    ).save()

    return _job_id


def delete_resource_from_graphite(res_name, res_type, integration_id, action):
    _job_id = str(uuid.uuid4())
    _params = {
        "TendrlContext.integration_id": NS.tendrl_context.integration_id,
        "TendrlContext.cluster_name": NS.tendrl_context.cluster_name,
        "Trigger.resource_name": res_name,
        "Trigger.resource_type": res_type,
        "Trigger.action": action
    }
    _job_payload = {
        "tags": ["tendrl/integration/monitoring"],
        "run": "monitoring.flows.DeleteResourceFromGraphite",
        "status": "new",
        "parameters": _params,
        "type": "monitoring"
    }
    NS.tendrl.objects.Job(
        job_id=_job_id,
        status="new",
        payload=_job_payload
    ).save()

    return _job_id
