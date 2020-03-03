import builtins
import maps
from tendrl.commons.utils.monitoring_utils import delete_resource_from_graphite
from tendrl.commons.utils.monitoring_utils import update_dashboard


# Create a MockObject class, acts similarly to the patch object and mock
# tools for testing.
class MockJob(object):

    def __init__(self, job_id=None, status=None, payload=None):
        self.locked_by = None
        self.status = status
        self.payload = payload
        self.job_id = job_id

    def save(self):
        pass


# Tests that the update_dashboard method runs
def test_update_dashboard():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = 0
    NS.tendrl_context.cluster_name = "Test Name"
    NS.tendrl.objects.Job = MockJob
    assert update_dashboard("Test Name", "Test", 0, "push")


# Tests that the delete resource from graphite method runs
def test_delete_resource_from_graphite():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = 0
    NS.tendrl_context.cluster_name = "Test Name"
    NS.tendrl.objects.Job = MockJob
    assert delete_resource_from_graphite("Test Name", "Test", 0, "push")
