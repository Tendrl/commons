from tendrl.commons.objects.cluster_alert import ClusterAlert


def test_render():
    cluster_alert_obj = ClusterAlert(
        tags={'integration_id': 'test_uuid'}
    )
    cluster_alert_obj.render()
