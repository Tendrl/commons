import __builtin__
import importlib
import maps
from mock import patch

from tendrl.commons.objects.cluster.atoms.setup_cluster_alias \
    import SetupClusterAlias
from tendrl.commons.objects.job import Job


def save(*args):
    pass


def load_job_finished(*args):
    return Job(job_id="uuid", status='finished')


def load_job_new(*args):
    return Job(job_id="uuid", status='new')


def init():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    obj = importlib.import_module("tendrl.commons.tests.fixtures.client")
    NS._int.client = obj.Client()
    NS._int.wclient = obj.Client()

    NS.node_context = maps.NamedDict()
    NS.node_context.tags = maps.NamedDict()
    NS._int.watchers = maps.NamedDict()


def test_run():
    init()
    sca_obj = SetupClusterAlias()
    sca_obj.parameters = maps.NamedDict()
    sca_obj.parameters['TendrlContext.integration_id'] = \
        'test_uuid'
    sca_obj.parameters['job_id'] = 'test_job_id'

    setattr(NS, "tendrl", maps.NamedDict())
    setattr(NS, "tendrl_context", maps.NamedDict())
    NS.tendrl_context['integration_id'] = "rete"
    setattr(NS.tendrl, "objects", maps.NamedDict(Job=Job))

    # provisioner not in tags
    with patch.object(NS.tendrl.objects.Job, 'save', save):
        with patch.object(Job, 'load', load_job_finished):
            sca_obj.run()

    # provisioner in tags, success
    NS.node_context.tags = "provisioner/test_uuid"
    with patch.object(NS.tendrl.objects.Job, 'save', save):
        with patch.object(Job, 'load', load_job_finished):
            sca_obj.run()

    # provisoner in tags, failure
    NS.publisher_id = maps.NamedDict()
    sca_obj.parameters['flow_id'] = 'test_flow_id'
    with patch.object(NS.tendrl.objects.Job, 'save', save):
        with patch.object(Job, 'load', load_job_new):
            sca_obj.run()
