import __builtin__
import maps
from mock import patch

from tendrl.commons.objects.node.atoms.check_node_up import CheckNodeUp
from tendrl.commons.utils.cmd_utils import Command
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


class MockJob(object):
    def __init__(self, job_id=None):
        pass

    def load(self):
        self.payload = {}
        return self


def false_run(*args):
    return "Test Out", '', 1


def run(*args):
    return "Test Out", '', 0


def read(key):
    if "tags" in key:
        out = maps.NamedDict(
            value=u'["fe80532d-95e0-4b10-b486-a357e325cccf"]'
        )
    elif "fqdn" in key:
        out = maps.NamedDict(
            value=u'dhcp12'
        )
    return out


# Testing run
@patch.object(logger, "log")
def test_run(log):
    log.return_value = True
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS["tendrl"] = maps.NamedDict()
    NS.tendrl["objects"] = maps.NamedDict(Job=MockJob)
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    check_node_up = CheckNodeUp()
    check_node_up.parameters = maps.NamedDict()
    check_node_up.parameters['TendrlContext.integration_id'] = \
        "7a3f2238-ef79-4943-9edf-762a80cf22a0"
    check_node_up.parameters['job_id'] = "node_job"
    check_node_up.parameters['flow_id'] = "flow_id"
    with patch.object(etcd_utils, "read", read):
        with patch.object(Command, "run", false_run):
            if check_node_up.run():
                raise AssertionError
        with patch.object(Command, "run", run):
            if not check_node_up.run():
                raise AssertionError
