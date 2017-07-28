import __builtin__
import maps


from tendrl.commons.objects.detected_cluster import DetectedCluster


def test_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''

    # Passing dummy values
    detected_cluster = DetectedCluster(detected_cluster_id=1,
                                       detected_cluster_name="Test Cluster",
                                       sds_pkg_name="Test package",
                                       sds_pkg_version=1.1)
    assert detected_cluster is not None
    assert detected_cluster.sds_pkg_name == "Test package"
    detected_cluster = DetectedCluster()
    assert detected_cluster.sds_pkg_name is None


# Testing render
def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    detected_cluster = DetectedCluster()
    assert detected_cluster.render() is not None
