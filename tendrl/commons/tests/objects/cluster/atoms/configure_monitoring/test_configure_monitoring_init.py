import __builtin__
import maps
import subprocess

from mock import patch

from tendrl.commons.objects.cluster.atoms.configure_monitoring import \
    ConfigureMonitoring


def init():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.config = maps.NamedDict()
    NS.config.data = maps.NamedDict()
    NS.node_context = maps.NamedDict()
    NS.node_context["fqdn"] = "localhost"
    NS.node_context["tags"] = maps.NamedDict()
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context["integration_id"] = "test"
    NS.tendrl_context["sds_name"] = "gluster"
    NS.node_context["node_id"] = "test"
    NS.config.data["logging_socket_path"] = "~/test"
    NS.config.data["sync_interval"] = "10"
    NS.config.data['etcd_connection'] = "test"
    NS.config.data["etcd_port"] = 8080
    NS.config.data["etcd_ca_cert_file"] = "test"
    NS.config.data["etcd_cert_file"] = "test"
    NS.config.data["etcd_key_file"] = "test"


@patch.object(subprocess, 'check_call')
def test_run(patch_check_call):
    patch_check_call.return_value = True
    init()
    test = ConfigureMonitoring()
    test.parameters = maps.NamedDict()
    test.parameters['job_id'] = 1729
    test.parameters['flow_id'] = 13
    test.run()


@patch.object(ConfigureMonitoring, '_configure_plugin')
def test_configure_plugin_fail(patch_check_call):
    patch_check_call.return_value = False
    init()
    test = ConfigureMonitoring()
    test.parameters = maps.NamedDict()
    test.parameters['job_id'] = 1729
    test.parameters['flow_id'] = 13
    ret_val = test.run()
    if ret_val:
        raise AssertionError
