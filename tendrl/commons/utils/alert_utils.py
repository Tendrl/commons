import json
import os

from tendrl.commons.utils import log_utils as logger
from tendrl.commons.utils.time_utils import now as tendrl_now


def alert_job_status(curr_value, msg, integration_id=None, cluster_name=None):
    alert = {}
    alert['source'] = NS.publisher_id
    alert['classification'] = 'cluster'
    alert['pid'] = os.getpid()
    alert['time_stamp'] = tendrl_now().isoformat()
    alert['alert_type'] = 'STATUS'
    severity = "INFO"
    if curr_value.lower() == "failed":
        severity = "WARNING"
    alert['severity'] = severity
    alert['resource'] = 'job_status'
    alert['current_value'] = curr_value
    alert['notify_only_ui'] = True
    alert['tags'] = dict(
        message=msg,
        integration_id=integration_id or
        NS.tendrl_context.integration_id,
        cluster_name=cluster_name or
        NS.tendrl_context.cluster_name,
        sds_name=NS.tendrl_context.sds_name,
        fqdn=NS.node_context.fqdn
    )
    alert['node_id'] = NS.node_context.node_id
    if not NS.node_context.node_id:
        return
    logger.log(
        "notice",
        "alerting",
        {'message': json.dumps(alert)}
    )
