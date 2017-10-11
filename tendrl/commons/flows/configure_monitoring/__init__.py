from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError


class ConfigureMonitoring(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(ConfigureMonitoring, self).__init__(*args, **kwargs)

    def run(self):
        _cluster = NS.tendrl.objects.Cluster(
            integration_id=NS.tendrl_context.integration_id
        ).load()
        if _cluster.is_managed != "yes":
            raise FlowExecutionFailedError('Cluster is not managed')
        self.parameters['Service.name'] = 'collectd'
        super(ConfigureMonitoring, self).run()
