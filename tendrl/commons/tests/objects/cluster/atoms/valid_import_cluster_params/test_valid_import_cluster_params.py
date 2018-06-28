import __builtin__
import maps
from tendrl.commons.objects.cluster.atoms.valid_import_cluster_params \
    import ValidImportClusterParams


def test_run():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = maps.NamedDict()
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = "test_integration_id"

    vicp_obj = ValidImportClusterParams()
    vicp_obj.parameters = maps.NamedDict()

    # success
    vicp_obj.parameters['TendrlContext.integration_id'] = 'test_integration_id'
    vicp_obj.run()

    # failure
    vicp_obj.parameters['TendrlContext.integration_id'] = None
    vicp_obj.job_id = 'test_job_id'
    vicp_obj.parameters['flow_id'] = 'test_flow_id'
    vicp_obj.run()
