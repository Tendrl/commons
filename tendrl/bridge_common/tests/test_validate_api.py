"""
test_validate_api
----------------------------------

Tests for `validate_api` module.
"""

import os
import sys

sys.path.insert(0, '../../')
from tendrl.bridge_common.JobValidator.api import ApiJobValidator
from tendrl.bridge_common import util


def getSchemaFile(schemaName):
    localpath = os.path.dirname(__file__)
    path = os.path.join(localpath, "sds_state_" + schemaName + '.yaml')
    # return yaml.load(open(path))
    return util.loadSchema(path)[1]


class TestValidateJobApi(object):

    def test_validate(self):
        # Success test
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_name": "gluster",
            "sds_version": "3.2.0",
            "flow": "CreateGlusterVolume",
            "status": "processing",
            "parameters": {
                'volname': 'Volume1',
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.validateApi(glusterApiJob)
        assert status

    def test_atom(self):
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.checkAtom("volume.atoms.start")
        assert error == "atom:start details not found for:volume"
        assert not status

    def test_flow(self):
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.checkFlow("StopVolume")
        assert error == "Flow: StopVolume not defined"
        assert not status

    def test_getAtomsFromAtom(self):
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        flow = sdsoper.getAtomNamesFromFlow("CreateGlusterVolume")
        assert flow[0] == "volume.atoms.create"

    def test_flowAttrs(self):
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        assert type(sdsoper.getFlowParms(
            "CreateGlusterVolume")) == type(tuple(""))

    def test_checkJobRequiredAttr(self):
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_name": "gluster",
            "sds_version": "3.2.0",
            "flow": "CreateGlusterVolume",
            "status": "processing",
            "parameters": {
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.checkJobRequiredParm(
            glusterApiJob['parameters'], ['volname', 'brickdetails'])
        assert error == "Missing input argument(s) ['volname']"

    def test_apijob_with_wrong_datatype(self):
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_name": "gluster",
            "sds_version": "3.2.0",
            "flow": "CreateGlusterVolume",
            "status": "processing",
            "parameters": {
                'volname': 'Volume1',
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        # Testing with invalid data type for strip_count
        glusterApiJob['parameters']['stripe_count'] = '10'
        status, error = sdsoper.validateApi(glusterApiJob)
        msg = "Invalid parameter type: stripe_count. "\
              "Expected value type is: Integer"
        assert error == msg
        assert not status

        glusterApiJob['parameters']['stripe_count'] = []
        status, error = sdsoper.validateApi(glusterApiJob)
        msg = "Invalid parameter type: stripe_count. "\
              "Expected value type is: Integer"
        assert error == msg
        assert not status

        glusterApiJob['parameters']['stripe_count'] = "RAID"
        status, error = sdsoper.validateApi(glusterApiJob)
        msg = "Invalid parameter type: stripe_count. "\
              "Expected value type is: Integer"
        assert error == msg
        assert not status

        # test with an unknown flow which is not defined
        glusterApiJob['flow'] = 'blabla'
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "Flow: blabla not defined"
        assert not status

    def test_apijob_without_required_arguments(self):
        # Volume name not provided
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_name": "gluster",
            "sds_version": "3.2.0",
            "flow": "CreateGlusterVolume",
            "status": "processing",
            "parameters": {
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "Missing input argument(s) ['volname']"
        assert not status

        glusterApiJob['parameters'].pop('stripe_count')
        status, error = sdsoper.validateApi(glusterApiJob)
        # stripe_count is an optional param
        assert error == "Missing input argument(s) ['volname']"
        assert not status

    def test_apijob_with_wrong_argument_name(self):
        # Invalid argument names passed which are not defined
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_name": "gluster",
            "sds_version": "3.2.0",
            "flow": "CreateGlusterVolume",
            "status": "processing",
            "parameters": {
                'myvolumename': 'testing',
                'volname': "test",
                'blabla': 100,
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error.find("argument(s) not defined") > 0
        assert error.find('myvolumename') > 0
        assert error.find('blabla') > 0
        assert not status

    def test_apijob_missing_argument(self):
        nodeApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "node_name": "fqdn",
            "node_version": "3.2.0",
            "flow": "PackageInstall",
            "status": "processing",
            "parameters": {'name': 'abc',
                           'list': ["wget", "rpm-build"],
                           'conf_file': "/etc/abc.conf",
                           'state': True,
                           'enablerepo': ["a1", "a2", "a3"],
                           'disablerepo': []},
        }
        sdsoper = ApiJobValidator(getSchemaFile("node"))
        status, error = sdsoper.validateApi(nodeApiJob)
        assert error == "Input argument(s) not defined " + "\
in yaml file: ['state']"
        assert not status
