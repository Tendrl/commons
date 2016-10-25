#
# Copyright 2016 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#

########################################################
#
#  Set of user defined validateApiJob exceptions.
#
########################################################

# from tendrl.exception import tendrlException


class ApiJobValidateException(Exception):
    code = 0
    message = "Api Job Validate Exception"

    def __init__(self, code=0, message='Api Job Validate Exception'):
        self.code = code
        self.message = message

    def __str__(self):
        return self.message

    def response(self):
        return {'status': {'code': self.code, 'message': str(self)}}


class FailedLoadingSchemaException(ApiJobValidateException):
    code = 1001
    message = "Unable to load the schema file"


class ValidObjectsNotFoundException(ApiJobValidateException):
    code = 1002
    message = "Valid objects not found in the yaml file"


class ObjectDetailsNotFoundException(ApiJobValidateException):
    code = 1003
    message = "Object details not found in the yaml file"


class FlowDetailsNotFoundException(ApiJobValidateException):
    code = 1004
    message = "Flow details not found in the yaml file"
