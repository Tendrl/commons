import __builtin__
import maps

from tendrl.commons.objects.cluster.atoms.check_sync_done import CheckSyncDone


class MockCNC(object):
    def __init__(self, node_id=1):
        self.first_sync_done = "yes"

    def load(self):
        return self


def init():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl.objects.ClusterNodeContext = MockCNC
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = "test"


def test_check_sync_done():
    init()
    test = CheckSyncDone()
    test.parameters = maps.NamedDict()
    test.parameters['TendrlContext'] = maps.NamedDict()
    test.parameters['TendrlContext.integration_id'] = \
        '94ac63ba-de73-4e7f-8dfa-9010d9554084'
    test.run()
