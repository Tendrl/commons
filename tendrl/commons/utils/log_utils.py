"""Handles logging functionality."""
from inspect import getframeinfo
from inspect import stack
import sys

from tendrl.commons.event import Event
from tendrl.commons.message import Message


def log(log_priority, publisher_id, log_payload, job_id=None,
        flow_id=None, parent_id=None, integration_id=None, node_id=None):
    """Function used for logging errors/output/info.

    Args:
        log_priority [Type : String]: Priority of the Log Message (error/info)
        publisher_id [Type : Integer] : Id of publisher (mandatory)
        log_payload [Type: Dict] : Payload can contain /
                                   parameters like message that is to be logged
    """
    caller_details = getframeinfo(stack()[1][0])
    caller_details = {"filename": caller_details.filename,
                      "line_no": caller_details.lineno,
                      "function": caller_details.function}
    try:
        Event(
            Message(
                log_priority, publisher_id, log_payload,
                job_id, flow_id, parent_id,
                integration_id or NS.tendrl_context.integration_id,
                caller=caller_details,
                node_id=node_id
            )
        )
    except Exception:
        if log_priority.lower() == "error":
            sys.stderr.write(log_payload.get("message", "") + "\n")
        else:
            sys.stdout.write(log_payload.get("message", "") + "\n")
