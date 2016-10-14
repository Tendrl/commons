"""
test_validate_api
----------------------------------

Tests for `validate_api` module.
"""

import os
import unittest
import sys
import mock

sys.path.insert(0, '../../')
import bridge_common.validateapi as apivalidate
from bridge_common.validateapi import SdsOperations

def getSchemaPath(schemaName):
    localpath = os.path.dirname(__file__)
    path = os.path.join(localpath, "sds_state_" + schemaName + '.yaml')
    return path


@mock.patch('bridge_common.validateapi.locateSchema', getSchemaPath)
class TestValidateApi(unittest.TestCase):

    def test_validate(self):
        # Success test
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'gluster',
            'flow': "create",
            'object_type': 'volume',
            'status': 'new',
            'message': 'Creating cluster',
            'attributes': {
                'volname': 'Volume1',
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = SdsOperations()
        status, error = sdsoper.validateApi(glusterApiJob)
        self.assertEqual(status, True)

    def test_apijob_with_wrong_datatype(self):
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'gluster',
            'flow': "create",
            'object_type': 'volume',
            'status': 'new',
            'message': 'Creating cluster',
            'attributes': {
                'volname': 'Volume1',
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = SdsOperations()
        # Testing with invalid data type for strip_count
        glusterApiJob['attributes']['stripe_count'] = '10'
        status, error = sdsoper.validateApi(glusterApiJob)
        self.assertEqual(error, "Invalid parameter type: stripe_count. Expected value type is: Integer")
        self.assertEqual(status, False)

        glusterApiJob['attributes']['stripe_count'] = []
        status, error = sdsoper.validateApi(glusterApiJob)
        self.assertEqual(error, "Invalid parameter type: stripe_count. Expected value type is: Integer")
        self.assertEqual(status, False)

        glusterApiJob['attributes']['stripe_count'] = "RAID"
        status, error = sdsoper.validateApi(glusterApiJob)
        self.assertEqual(error, "Invalid parameter type: stripe_count. Expected value type is: Integer")
        self.assertEqual(status, False)

    def test_apijob_without_required_arguments(self):
        # Volume name not provided
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'gluster',
            'flow': "create",
            'object_type': 'volume',
            'status': 'new',
            'message': 'Creating cluster',
            'attributes': {
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = SdsOperations()
        status, error = sdsoper.validateApi(glusterApiJob)
        self.assertEqual(error, "Missing input argument(s) ['volname']")
        self.assertEqual(status, False)

        glusterApiJob['attributes'].pop('stripe_count')
        status, error = sdsoper.validateApi(glusterApiJob)
        self.assertEqual(error, "Missing input argument(s) ['volname', 'stripe_count']")
        self.assertEqual(status, False)

    def test_apijob_with_wrong_argument_name(self):
        # Invalid argument names passed which are not defined
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'gluster',
            'flow': "create",
            'object_type': 'volume',
            'status': 'new',
            'message': 'Creating cluster',
            'attributes': {
                'myvolumename': 'testing',
                'volname': "test",
                'blabla': 100,
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = SdsOperations()
        status, error = sdsoper.validateApi(glusterApiJob)
        self.assertEqual(error, "Input argument(s) not defined in yaml file: ['myvolumename', 'blabla']")
        self.assertEqual(status, False)

    def test_apijob_with_other_operational_yaml(self):
        # success test
        nodeApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'node',
            'flow': "dnf",
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
        sdsoper = SdsOperations()
        status, error = sdsoper.validateApi(nodeApiJob)
        self.assertEqual(status, True)

    def test_apijob_missing_arguments(self):
        nodeApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'node',
            'flow': "dnf",
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
        sdsoper = SdsOperations()
        status, error = sdsoper.validateApi(nodeApiJob)
        self.assertEqual(status, False)
        self.assertEqual(error, "Missing input argument(s) ['list', 'disable_gpg_check']")

    def test_apijob__arguments_not_defined(self):
        nodeApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            'sds_type': 'node',
            'flow': "dnf",
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
        sdsoper = SdsOperations()
        status, error = sdsoper.validateApi(nodeApiJob)
        self.assertEqual(status, False)
        self.assertEqual(error, "Input argument(s) not defined in yaml file: ['newvalue']")
