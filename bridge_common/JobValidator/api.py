#!/usr/bin/python
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license

# Usage: opr = SdsOperations()
#        opr.validateApi(api-job)
# This api can be used to validate the api-job against the
# perdefined sds_operation_schema in the yaml file.


import os
import six
import yaml


PRIMITIVE_TYPES = {'Boolean': lambda value: isinstance(value, bool),
                   'Float': lambda value: isinstance(value, float),
                   'Integer': lambda value: isinstance(value, int),
                   'Long': lambda value: isinstance(value, (
                       six.integer_types, float)),
                   'String': lambda value: isinstance(value, six.string_types),
                   'Uint': lambda value: isinstance(value, int) and value >= 0,
                   'List': lambda value: isinstance(value, list)}


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


def loadSchema(schemaFile):
    try:
        # Check api operation schema file exists
        if not os.path.isfile(schemaFile):
            return (False,
                    "Error: Schema file '" + schemaFile + "' does not exists.")

        # load api operation schema file and return
        try:
            code = open(schemaFile)
        except IOError as exc:
            return (False,
                    "Error loading schema file '" + schemaFile + "': " + exc)

        # Parse schema file
        try:
            config = yaml.load(code)
        except yaml.YAMLError as exc:
            error_pos = ""
            if hasattr(exc, 'problem_mark'):
                error_pos = " at position: (%s:%s)" % (
                    exc.problem_mark.line + 1,
                    exc.problem_mark.column + 1)
            msg = "Error loading schema file '" + schemaFile + "'" + error_pos \
                + ": content format error: Failed to parse yaml format"
            return False, msg

    except Exception as e:
        return (False, "Error loading api operation schema file '%s': %s" % (
            schemaFile, str(e)))

    return (True, config)


class ApiJobValidator(object):
    def __init__(self, schemaFilePath):
        self.yamlObj = None
        status = loadSchema(schemaFilePath)
        # load schema into memory only on success
        if not status[0]:
            raise FailedLoadingSchemaException(1, status[1])
        # validate yaml schema file
        if not status[1].get('valid_objects'):
            raise ValidObjectsNotFoundException()
        if not status[1].get('object_details'):
            raise ObjectDetailsNotFoundException()
        if not status[1].get('flows'):
            raise FlowDetailsNotFoundException()
        self.yamlObj = status[1]

    def checkFlow(self, flowName):
        # Check flow exists
        flow = self.yamlObj['flows'].get(flowName)
        if not flow:
            return (False, "Flow: %s not defined" % (flowName))
        # Check flow enabled
        if flow.get('enabled') is not True:
            return (False, "Flow: %s not enabled" % (flowName))
        # Check uuid exists
        if 'uuid' not in flow:
            return (False, "uuid not found for the flow: %s" % (flowName))
        # Check atoms exists
        if 'atoms' not in flow:
            return (False, "atoms not found for the flow: %s" % (flowName))
        return (True, '')

    def checkAtom(self, atom):
        # Check object defined in yaml
        objName, con, oper = atom.split('.')
        obj = self.yamlObj.get('object_details', {}).get(objName, {})
        if not obj:
            return (False,
                    "object atom details not found for:%s" % (objName))
        obj = obj.get(con, {}).get(oper, {})
        # Check whether atoms defined
        if not obj:
            return (False,
                    "atom:%s details not found for:%s" % (oper, objName))
        if 'uuid' not in obj:
            return (False,
                    "uuid not found for the atom:%s.%s" % (objName, atom))
        return (True, '')

    def getAtomNamesFromFlow(self, flow):
        return self.yamlObj.get('flows', {}).get(
            flow, {}).get('atoms', {})

    def checkJobRequiredParm(self, gvnParm, reqParm):
        # gvnParm is the list of given parameters for a job request
        # reqParm is the required parms for the job mentioned in yaml
        reqParm = [p.split(".")[-1] for p in reqParm]
        missingInputParm = set(reqParm).difference(set(gvnParm))
        if missingInputParm != set():
            return (False,
                    "Missing input argument(s) %s" % (list(missingInputParm)))
        return(True, '')

    def checkJobParmDefined(self, gvnParm, docParm):
        # checking whether given arguments are defined in the yaml file
        docParm = [p.split(".")[-1] for p in docParm]
        missingConfigParm = set(gvnParm).difference(set(docParm))
        if missingConfigParm != set():
            return (False, "Input argument(s) not defined in yaml file: %s" % (
                list(missingConfigParm)))
        return (True, '')

    def getParmPath(self, gvnParm, docParm):
        iParmAndObj = {}
        for p in docParm:
            if p.split('.')[-1] in gvnParm:
                iParmAndObj[p] = gvnParm[p.split('.')[-1]]
        return iParmAndObj

    def checkParmType(self, gvnParm, parmRequired=True):
        # Check the given input parameter's type using
        # the parameters of the object type.
        objTypeName, parmName = gvnParm.split(".")
        parms = self.yamlObj['object_details'][objTypeName]['attrs']
        if gvnParm not in parms:
            if parmRequired:
                return (False, "Given input parameters" +
                        ":%s not defined" % (gvnParm))
            # else (pass) Its an optional parameter

    def checkInputType(self, gvnParm):
        # Check the given input parameter's type using
        # the parameters of the object type.
        for parm, val in gvnParm.items():
            # Some arguments does not required any purticular type.
            # Contine validating next parm if the type of the
            # inputparm not defined in yaml.
            iObjType, iParm = parm.split(".")
            
            parms = self.yamlObj['object_details'][iObjType]['attrs']
            if iParm not in parms:
                continue
            expectedType = parms[iParm].get('type')
            # A) Check whether given value type is custom type
            if expectedType not in PRIMITIVE_TYPES.keys():
                status = self._checkCustomType(expectedType,
                                               iParm,
                                               val)
                if status[0]:
                    # continue to validate remaining parm
                    continue
                else:
                    return status
            # B) General type parameters
            # Check the given value type is valid and
            # its matched with the required type defined in yaml
            if not PRIMITIVE_TYPES[expectedType](val):
                return (False, "Invalid parameter type: "
                        + "%s. Expected value type is: %s" % (
                            iParm, expectedType))
        return(True, "")

    def getFlowParms(self, flowName):
        """ This function will return mandatory and
        optional parameters of the given flow from the loaded yaml"""
        return (self.yamlObj.get("flows", {}).get(
            flowName, {}).get("inputs", {}).get("mandatory"),
            self.yamlObj.get("flows", {}).get(
                flowName, {}).get("inputs", {}).get("optional"))

    def getAtomParms(self, atom):
        """ This function will return mandatory and
        optional parameters of the given atom from the loaded yaml"""
        objType, con, atomName = atom.split(".")
        return (self.yamlObj.get("object_details", {}).get(
            objType, {}).get(con, {}).get(atomName, {}).get(
                "inputs",{}).get("mandatory"),
                self.yamlObj.get("object_details", {}).get(
                    objType, {}).get(con, {}).get(atomName, {}).get(
                        "inputs", {}).get("optional"))

    def _checkCustomType(self, customType, inputParm, inputVal):
        def _check(inputVal, cType=customType):
            # check whether the custom defined type is decleared!
            typeDef = self.yamlObj.get('object_details').get(cType.lower())
            if not typeDef:
                return (False, "yaml custom type: '%s' details not found" % (
                    cType))

            # check whether the item(s) type is valid
            for item in inputVal:
                itemType = typeDef['attrs'].get(inputParm, {}).get('type')
                if not PRIMITIVE_TYPES[itemType](item):
                    return (False, "Invalid parameter type: "
                            + "%s. Expected value type is: %s" % (
                                item, itemType))
            return (True, "")

        # customType is an array
        if customType.endswith('[]'):
            # check whether the given input is an array
            if not PRIMITIVE_TYPES['List'](inputVal):
                return (False, "Invalid input type: %s. " % (
                    inputVal) + " Expected value type is an array")
            return _check(inputVal, customType[:-2])
        else:
            # Its a non-array custom type
            return _check([inputVal])

    def validateApi(self, apiJob):
        if not self.yamlObj:
            return (False, "Validating schema not loaded!")

        if "cluster_id" not in apiJob:
            return (False, "Cluster id not found in the api job")
        if "flow" not in apiJob:
            return (False, "flow not found in the api job")
        if "parameters" not in apiJob:
            return (False, "parameters not found in the api job")

        # Checking flow details!
        status = self.checkFlow(apiJob["flow"])
        if not status[0]:
            return status
        reqParm, optParm = self.getFlowParms(apiJob["flow"])
        # no need to check anything if no parameters are required
        if reqParm:
            # check whether all the required parameters are given
            status = self.checkJobRequiredParm(apiJob["parameters"], reqParm)
            if not status[0]:
                return status
            # check whether all the parameters are defined in yaml
            status = self.checkJobParmDefined(apiJob["parameters"],
                                              reqParm + optParm)
            if not status[0]:
                return status
            # check given parameters type
            inputParmWithObj = self.getParmPath(apiJob["parameters"],
                                                reqParm + optParm)
            status = self.checkInputType(inputParmWithObj)
            if not status[0]:
                return status

        # Checking atoms of the flow
        atoms = self.getAtomNamesFromFlow(apiJob["flow"])
        if not atoms:
            return (False,
                    "flow:%d does not have any atom defined" % apiJob["flow"])
        for atom in atoms:
            status = self.checkAtom(atom)
            if not status[0]:
                return status
            reqParm, optParm =  self.getAtomParms(atom)
            if not reqParm:
                return (True, '')
            # check whether all the required parameters are given
            status = self.checkJobRequiredParm(apiJob["parameters"], reqParm)
            if not status[0]:
                return status
            # check whether all the parameters are defined in yaml
            status = self.checkJobParmDefined(apiJob["parameters"],
                                              reqParm + optParm)
            if not status[0]:
                return status
            # check given parameters type
            inputParmWithObj = self.getParmPath(apiJob["parameters"],
                                                reqParm + optParm)
            status = self.checkInputType(inputParmWithObj)
            if not status[0]:
                return status
        # all check passed successfully!
        return(True, '')
