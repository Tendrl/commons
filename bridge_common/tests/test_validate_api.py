"""
test_validate_api
----------------------------------

Tests for `validate_api` module.
"""

import os
import sys

sys.path.insert(0, '../../')
from bridge_common.validate_job_api import ApiJobValidator
ApiJobValidator.MISSING_YAML_CHECK = True


def getSchemaFile(schemaName):
    localpath = os.path.dirname(__file__)
    path = os.path.join(localpath, "sds_state_" + schemaName + '.yaml')
    return path


class TestValidateJobApi(object):

    def test_validate(self):
        # Success test
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'gluster',
            'flow': "CreateGlusterVolume",
            'object_type': 'volume',
            'status': 'new',
            'message': 'Creating Gluster Volume',
            'attributes': {
                'volname': 'Volume1',
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.validateApi(glusterApiJob)
        assert status

    def test_apijob_with_wrong_datatype(self):
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'gluster',
            'flow': "CreateGlusterVolume",
            'object_type': 'volume',
            'status': 'new',
            'message': 'Creating volume',
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
        assert error == "Invalid parameter type: stripe_count. Expected value type is: Integer"
        assert not status

        glusterApiJob['attributes']['stripe_count'] = []
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "Invalid parameter type: stripe_count. Expected value type is: Integer"
        assert not status

        glusterApiJob['attributes']['stripe_count'] = "RAID"
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "Invalid parameter type: stripe_count. Expected value type is: Integer"
        assert not status

        # change flow name which is not defined
        glusterApiJob['flow'] = 'blabla'
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "Flow: blabla not defined in the yaml flows"
        assert not status

    def test_apijob_without_required_arguments(self):
        # Volume name not provided
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'gluster',
            'flow': "CreateGlusterVolume",
            'object_type': 'volume',
            'status': 'new',
            'message': 'Creating volume',
            'attributes': {
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"), True)
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "Missing input argument(s) ['volname']"
        assert not status

        glusterApiJob['attributes'].pop('stripe_count')
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "Missing input argument(s) ['volname', 'stripe_count']"
        assert not status

    def test_apijob_with_wrong_argument_name(self):
        # Invalid argument names passed which are not defined
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'gluster',
            'flow': "CreateGlusterVolume",
            'object_type': 'volume',
            'status': 'new',
            'message': 'Creating volume',
            'attributes': {
                'myvolumename': 'testing',
                'volname': "test",
                'blabla': 100,
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = ApiJobValidator(getSchemaFile("gluster"), True)
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "Input argument(s) not defined in yaml file: ['myvolumename', 'blabla']"
        assert not status

    def test_apijob_with_other_operational_yaml(self):
        # success test
        nodeApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'node',
            'flow': 'PackageInstall',
            'object_type': 'general',
            'status': 'new',
            'message': 'Installing Packages',
            'attributes': {
                'name': 'abc',
                'list': ["wget", "rpm-build"],
                'disable_gpg_check': True,
                'conf_file': "/etc/abc.conf",
                'state': True,
                'enablerepo': ["a1", "a2", "a3"],
                'disablerepo': []},
            'errors': {}
        }
        sdsoper = ApiJobValidator(getSchemaFile("node"))
        status, error = sdsoper.validateApi(nodeApiJob)
        assert status

    def test_apijob_missing_arguments(self):
        nodeApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'node',
            'flow': 'PackageInstall',
            'object_type': 'general',
            'status': 'new',
            'message': 'Installing Packages',
            'attributes': {
                'name': 'abc',
                'conf_file': "/etc/abc.conf",
                'state': True,
                'enablerepo': ["a1", "a2", "a3"],
                'disablerepo': []},
            'errors': {}
        }
        sdsoper = ApiJobValidator(getSchemaFile("node"), True)
        status, error = sdsoper.validateApi(nodeApiJob)
        assert not status
        assert error == "Missing input argument(s) ['list', 'disable_gpg_check']"

    def test_apijob__arguments_not_defined(self):
        nodeApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'node',
            'flow': 'PackageInstall',
            'object_type': 'general',
            'status': 'new',
            'message': 'Installing Packages',
            'attributes': {
                'name': 'abc',
                'list': ["wget", "rpm-build"],
                'disable_gpg_check': True,
                'conf_file': "/etc/abc.conf",
                'state': True,
                'enablerepo': ["a1", "a2", "a3"],
                'disablerepo': [],
                'newvalue': None},
            'errors': {}
        }
        sdsoper = ApiJobValidator(getSchemaFile("node"), True)
        status, error = sdsoper.validateApi(nodeApiJob)
        assert not status
        assert error == "Input argument(s) not defined in yaml file: ['newvalue']"
