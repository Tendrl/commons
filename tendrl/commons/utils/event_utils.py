import json
import os

from tendrl.commons.utils import log_utils as logger
from tendrl.commons.utils.time_utils import now as tendrl_now

BRICK_ENTITY = "brick"
VOLUME_ENTITY = "volume"


def emit_event(resource, curr_value, msg, instance,
               severity, alert_notify=False, tags={},
               integration_id=None, cluster_name=None,
               sds_name=None, node_id=None):
    alert = {}
    alert['source'] = NS.publisher_id
    alert['node_id'] = node_id
    alert['pid'] = os.getpid()
    alert['time_stamp'] = tendrl_now().isoformat()
    alert['alert_type'] = 'STATUS'
    alert['severity'] = severity
    alert['resource'] = resource
    alert['current_value'] = curr_value
    alert['tags'] = dict(
        plugin_instance=instance,
        message=msg,
        integration_id=integration_id or NS.tendrl_context.integration_id,
        cluster_name=cluster_name or NS.tendrl_context.cluster_name
    )
    if "entity_type" in tags:
        if tags["entity_type"] == BRICK_ENTITY:
            alert['node_id'] = tags.get(
                "node_id", NS.node_context.node_id
            )
            alert['tags']['fqdn'] = tags.get(
                "fqdn", NS.node_context.fqdn
            )
            alert['tags']['volume_name'] = tags.get(
                'volume_name', None
            )
        elif tags["entity_type"] == VOLUME_ENTITY:
            alert['tags']['volume_name'] = tags.get(
                'volume_name', None
            )
    payload = {'message': json.dumps(alert)}
    payload['alert_condition_state'] = severity
    payload['alert_condition_status'] = resource

    if alert_notify:
        payload['alert_notify'] = alert_notify

    if severity == "INFO":
        payload['alert_condition_unset'] = True
    else:
        payload['alert_condition_unset'] = False
    logger.log(
        "notice",
        "alerting",
        payload,
        integration_id=integration_id
    )
