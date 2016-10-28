"""
test_validate_api
----------------------------------

Tests for `validate_api` module.
"""

import os
import sys

sys.path.insert(0, '../../')
from bridge_common.JobValidator.api import ApiJobValidator


def getSchemaFile(schemaName):
    localpath = os.path.dirname(__file__)
    path = os.path.join(localpath, "sds_state_" + schemaName + '.yaml')
    return path


class TestValidateJobApi(object):

    def test_validate(self):
        # Success test
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_nvr": "gluster-3.2",
            "action": "create",
            'object_type': 'volume',
            'status': 'new',
            'attributes': {
                'volname': 'Volume1',
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.validateApi(glusterApiJob)
        assert status

    def test_atom(self):
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.checkAtom("start", "volume")
        assert error == "atom:start details not found in the object:volume"
        assert not status

        status, error = sdsoper.checkAtom("stop", "volume")
        assert error == "atom:volume.stop does not have any flow"
        assert not status

    def test_flow(self):
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.checkFlow("StopVolume")
        assert error == "Flow: StopVolume not defined"
        assert not status

    def test_getFlowFromAtom(self):
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        flow = sdsoper.getFlowFromAtom("create", "volume")
        assert flow['flows'][0] == "CreateVolume"

    def test_flowAttrs(self):
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        assert type(sdsoper.getFlowAttrs(
            "CreateVolume")) == type(tuple(""))

    def test_checkJobRequiredAttr(self):
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_nvr": "gluster-3.2",
            "action": "create",
            'object_type': 'volume',
            'status': 'new',
            'attributes': {
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.checkJobRequiredAttr(
            glusterApiJob['attributes'], ['volname', 'brickdetails'])
        assert error == "Missing input argument(s) ['volname']"

    def test_apijob_with_wrong_datatype(self):
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_nvr": "gluster-3.2",
            "action": "create",
            'object_type': 'volume',
            'status': 'processing',
            'attributes': {
                'volname': 'Volume1',
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        # Testing with invalid data type for strip_count
        glusterApiJob['attributes']['stripe_count'] = '10'
        status, error = sdsoper.validateApi(glusterApiJob)
        msg = "Invalid parameter type: stripe_count. "\
              "Expected value type is: Integer"
        assert error == msg
        assert not status

        glusterApiJob['attributes']['stripe_count'] = []
        status, error = sdsoper.validateApi(glusterApiJob)
        msg = "Invalid parameter type: stripe_count. "\
              "Expected value type is: Integer"
        assert error == msg
        assert not status

        glusterApiJob['attributes']['stripe_count'] = "RAID"
        status, error = sdsoper.validateApi(glusterApiJob)
        msg = "Invalid parameter type: stripe_count. "\
              "Expected value type is: Integer"
        assert error == msg
        assert not status

        # test with an unknown action which is not defined
        glusterApiJob['action'] = 'blabla'
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "atom:blabla details not found in the object:volume"
        assert not status

    def test_apijob_without_required_arguments(self):
        # Volume name not provided
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_nvr": "gluster-3.2",
            "action": "create",
            'object_type': 'volume',
            'status': 'processing',
            'attributes': {
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "Missing input argument(s) ['volname']"
        assert not status

        glusterApiJob['attributes'].pop('stripe_count')
        status, error = sdsoper.validateApi(glusterApiJob)
        # stripe_count is an optional param
        assert error == "Missing input argument(s) ['volname']"
        assert not status

        glusterApiJob['attributes'].pop('brickdetails')
        status, error = sdsoper.validateApi(glusterApiJob)
        # stripe_count is an optional param
        assert error == "Missing input argument(s) ['volname', 'brickdetails']"
        assert not status

    def test_apijob_with_wrong_argument_name(self):
        # Invalid argument names passed which are not defined
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_nvr": "gluster-3.2",
            'object_type': 'volume',
            'status': 'processing',
            'attributes': {
                'myvolumename': 'testing',
                'volname': "test",
                'blabla': 100,
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "action not found in the api job"

        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "action not found in the api job"

        glusterApiJob["action"] = "create"
        glusterApiJob["attributes"]["testvar"] = "blabla"
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "Input argument(s) not defined in yaml file: "\
            "['testvar', 'myvolumename', 'blabla']"
        assert not status

        def test_apijob_missing_argument(self):
            nodeApiJob = {
                'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
                "node_agent_nvr": "tendrl-node-agent-3.2",
                'action': 'dnf',
                'object_type': 'general',
                'status': 'processing',
                'attributes': {
                    'name': 'abc',
                    'list': ["wget", "rpm-build"],
                    'conf_file': "/etc/abc.conf",
                    'state': True,
                    'enablerepo': ["a1", "a2", "a3"],
                    'disablerepo': []},
            }
            sdsoper = ApiJobValidator(getSchemaFile("node"))
            status, error = sdsoper.validateApi(nodeApiJob)
            assert error == "Input argument(s) not defined "
            + "in yaml file: ['state']"
            assert not status

        def test_apijob_attribute_not_found(self):
            nodeApiJob = {
                'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
                "node_agent_nvr": "tendrl-node-agent-3.2",
                'action': 'dnf',
                'object_type': 'general',
                'status': 'processing',
            }
            sdsoper = ApiJobValidator(getSchemaFile("node"))
            status, error = sdsoper.validateApi(nodeApiJob)
            assert error == "Input argument(s) not defined "
            + "in yaml file: ['state']"
            assert not status
