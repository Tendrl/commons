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
import exception as ex

PRIMITIVE_TYPES = {'Boolean': lambda value: isinstance(value, bool),
                   'Float': lambda value: isinstance(value, float),
                   'Integer': lambda value: isinstance(value, int),
                   'Long': lambda value: isinstance(value, (
                       six.integer_types, float)),
                   'String': lambda value: isinstance(value, six.string_types),
                   'Uint': lambda value: isinstance(value, int) and value >= 0,
                   'List': lambda value: isinstance(value, list)}


def loadSchema(schemaFile):
    try:
        # Check api operation schema file exists
        if not os.path.isfile(schemaFile):
            return (False,
                    "Error: Schema file '" + schemaFile + "' does not exists.")

        # load api operation schema file and return
        try:
            code = open(schemaFile)
        except IOError, exc:
            return (False,
                    "Error loading schema file '" + schemaFile + "': " + exc)

        # Parse schema file
        try:
            config = yaml.load(code)
        except yaml.YAMLError, exc:
            error_pos = ""
            if hasattr(exc, 'problem_mark'):
                error_pos = " at position: (%s:%s)" % (
                    exc.problem_mark.line+1,
                    exc.problem_mark.column+1)
            msg = "Error loading schema file '" + schemaFile + "'" + error_pos \
                + ": content format error: Failed to parse yaml format"
            return False, msg

    except Exception, e:
        return (False, "Error loading api operation schema file '%s': %s" % (
            schemaFile, str(e)))

    return (True, config)


class ApiJobValidator(object):
    def __init__(self, schemaFilePath):
        self.yamlObj = None
        status = loadSchema(schemaFilePath)
        # load schema into memory only on success
        if not status[0]:
            raise ex.FailedLoadingSchemaException(1, status[1])
        # validate yaml schema file
        if not status[1].get('valid_objects'):
            raise ex.ValidObjectsNotFoundException()
        if not status[1].get('object_details'):
            raise ex.ObjectDetailsNotFoundException()
        if not status[1].get('flows'):
            raise ex.FlowDetailsNotFoundException()
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

    def checkAtom(self, atom, objType=None):
        if not objType:
            if atom.find('.') < -1:
                return (False, "object name not specified"
                        + "for the atom: %s" % (atom))
            else:
                objType, atom = atom.split('.')
        # Check object defined in yaml
        obj = self.yamlObj.get('object_details', {})
        if not obj.get(objType):
            return (False,
                    "object details not found for the object type: %s" % (
                        objType))
        # Check whether atoms defined
        if not obj.get(objType, {}).get('atoms', {}).get(atom):
            return (False,
                    "atom:%s details not found in the object:%s" % (
                        atom, objType))
        if 'uuid' not in obj.get(objType).get('atoms').get(atom):
            return (False,
                    "uuid not found for the atom:%s.%s" % (objType, atom))
        if 'flows' not in obj.get(objType).get('atoms').get(atom):
            return (False,
                    "atom:%s.%s does not have any flow" % (objType, atom))
        if 'uuid' not in obj.get(objType).get('atoms').get(atom):
            return (False,
                    "uuid not found for the atom:%s" % (atom))
        return (True, '')

    def getFlowFromAtom(self, atom, objType):
        return self.yamlObj.get('object_details', {}).get(
            objType, {}).get('atoms', {}).get(atom)

    def checkJobRequiredAttr(self, gvnAttr, reqAttr):
        # gvnAttr is the list of given attribute for a job request
        # reqAttr is the required attribute for the job mentioned in yaml
        missingInputParm = set(reqAttr).difference(set(gvnAttr))
        if missingInputParm != set():
            return (False,
                    "Missing input argument(s) %s" % (list(missingInputParm)))
        return(True, '')

    def checkJobAttrDefined(self, gvnAttr, docAttr):
        # checking whether given arguments are defined in the yaml file
        missingConfigParm = set(gvnAttr).difference(set(docAttr))
        if missingConfigParm != set():
            return (False, "Input argument(s) not defined in yaml file: %s" % (
                list(missingConfigParm)))
        return (True, '')

    def checkInputType(self, objTypeName, gvnAttr):
        # Check the given input parameter's type using
        # the attributes of the object type.
        attrs = self.yamlObj['object_details'][objTypeName]['attrs']
        for inputParm, inputVal in gvnAttr.items():
            # Some arguments does not required any purticular type.
            # Contine validating next parm if the type of the
            # inputparm not defined in yaml.
            if inputParm not in attrs:
                continue
            expectedType = attrs[inputParm].get('type')
            # A) Check whether given value type is custom type
            if expectedType not in PRIMITIVE_TYPES.keys():
                status = self._checkCustomType(expectedType,
                                               inputParm,
                                               inputVal)
                if status[0]:
                    # continue to validate remaining attr
                    continue
                else:
                    return status
            # B) General type attributes
            # Check the given value type is valid and
            # its matched with the required type defined in yaml
            if not PRIMITIVE_TYPES[expectedType](inputVal):
                return (False, "Invalid parameter type: "
                        + "%s. Expected value type is: %s" % (
                            inputParm, expectedType))
        return(True, "")

    def getFlowAttrs(self, flowName):
        return (self.yamlObj.get("flows", {}).get(
            flowName, {}).get("inputs", {}).get("mandatory"),
            self.yamlObj.get("flows", {}).get(
                flowName, {}).get("inputs", {}).get("optional"))

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
        if "action" not in apiJob:
            return (False, "action not found in the api job")
        if "object_type" not in apiJob:
            return (False, "object type not found in the api job")
        if "attributes" not in apiJob:
            return (False, "attributes not found in the api job")

        status = self.checkAtom(apiJob["action"], apiJob["object_type"])
        if not status[0]:
            return status

        atom = self.getFlowFromAtom(apiJob["action"], apiJob["object_type"])
        flows = atom['flows']

        for flowName in flows:
            status = self.checkFlow(flowName)
            if not status[0]:
                return status

            reqAttr, optAttr = self.getFlowAttrs(flowName)
            # no need to check anything if no parameters are required
            if not reqAttr:
                continue  # for next flow

            # check whether all the required attributes are given
            status = self.checkJobRequiredAttr(apiJob["attributes"], reqAttr)
            if not status[0]:
                return status

            # check whether all the attributes are defined in yaml
            status = self.checkJobAttrDefined(apiJob["attributes"],
                                              reqAttr + optAttr)
            if not status[0]:
                return status

            # check the given attributes type
            status = self.checkInputType(apiJob["object_type"],
                                         apiJob["attributes"])
            if not status[0]:
                return status
        # all check passed successfully!
        return(True, '')
