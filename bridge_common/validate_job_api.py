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
    def __init__(self, schemaFilePath, chkMissingYaml=False):
        self.yamlObj = None
        self.chkMissingYaml = chkMissingYaml
        status = loadSchema(schemaFilePath)
        if not status[0]:
            raise ex.FailedLoadingSchemaException(1, status[1])
        yamlConf = status[1]

        # validate yaml schema file
        if not yamlConf.get('valid_objects'):
            raise ex.ValidObjectsNotFoundException()

        if not yamlConf.get('object_details'):
            raise ex.ObjectDetailsNotFoundException()

        if not yamlConf.get('object_details', {}).get("flows"):
            raise ex.FlowDetailsNotFoundException()

        # load the schema object into memory
        self.yamlObj = yamlConf.get('object_details')

    def _validateApiJob(self, apiJob):
        if not isinstance(apiJob, dict) or 'flow' not in apiJob:
            return (False, "Invalid request. Api Job Flow details not found")
        if 'sds_type' not in apiJob:
            return (False, "Invalid request. Api Job sds type not found")
        if 'object_type' not in apiJob:
            return (False, "Invalid request. Api Job object type not found")
        return (True, "")

    def _checkCustomType(self, customType, inputParm, inputVal):
        def _check(inputVal, cType=customType):
            # check whether the custom defined type is decleared!
            typeDef = self.yamlObj.get(cType.lower())
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

    def _getTag(self, dotPath):
        path = self.yamlObj
        for p in dotPath.split('.'):
            path = path.get(p, {})
        return path

    def validateApi(self, apiJob):
        if not self.yamlObj:
            return (False, "Validating schema not loaded!")

        status = self._validateApiJob(apiJob)
        if not status[0]:
            return status

        # Check object type defined
        if apiJob['object_type'] not in self.yamlObj:
            return (False, "Given object type:%s not defined in the yaml" % (
                apiJob['object_type']))

        # Check flow exists
        flow = self.yamlObj['flows'].get(apiJob.get('flow'))
        if not flow:
            return (False, "Flow: %s not defined in the yaml flows" % (
                apiJob['flow']))

        # A flow can have multiple automs defined
        # Validate list of atoms assigned for the flow
        for fatms in flow['atoms']:
            # check whether specified atom in the flows are found in atoms
            atom = self._getTag(fatms)
            if not atom:
                return (False, "Atom: %s not found for the flow: %s" % (
                    fatms, apiJob.get('flow')))

            # check whether given flow is defined in the atoms
            # atom = self.yamlObj[apiJob['object_type']]['atoms']
            if apiJob['flow'] not in atom.get('flows'):
                return (False, "Flow: %s not defined in atoms" % (
                    apiJob['flow']))

            # check whether given api-job has any arguments to check
            # or any arguments defined for this purticular job in the yaml.
            if 'inputs' not in atom or 'attributes' not in apiJob:
                return (True, "")

            # fetch the list of optional and required defined list from yaml
            defReqLst = []
            defOptLst = []
            for inputs in atom['inputs']:
                defReqLst += [k.split(".")[-1] for k, v in
                              inputs.items() if v['required']]
                defOptLst += [k.split(".")[-1] for k, v in
                              inputs.items() if not v['required']]

            # optain the given optional and remaining input param
            # from the given api job struct
            gvnLst = [i for i in
                      apiJob['attributes'].keys() if i not in defOptLst]

            # check whether any required argument is missing.
            # check the list of arguments given by api-job with the
            # list of required argument mentioned under flow tag in the yaml.
            missingInputParm = set(defReqLst).difference(set(gvnLst))
            if missingInputParm != set():
                return (False,
                        "Missing input argument(s) %s" % (list(
                            missingInputParm)))

            # checking whether given arguments are defined in the yaml file
            # is not required if multiple validation comes into picture.
            # Because one operaton might required some argument where as
            # another operation (atom) of the flow might not use it.
            missingConfigParm = set(gvnLst).difference(set(defReqLst))
            if self.chkMissingYaml and missingConfigParm != set():
                return (
                    False, "Input argument(s) not defined in yaml file: %s" % (
                        list(missingConfigParm)))

            if not self.yamlObj[apiJob['object_type']].get('attrs'):
                return (False, "Attributes not defined for this object: %s" % (
                    apiJob['object_type']))
            # verify whether argument value align with required type.
            # collect the attribute name and its type and check with the
            # type mentioned in the yaml file for the variable name.
            attrs = self.yamlObj[apiJob['object_type']]['attrs']
            for inputParm, inputVal in apiJob['attributes'].items():
                # Some arguments does not required any purticular type.
                # Contine validating next parm if the type of the
                # inputparm not defined in yaml.
                if inputParm not in attrs:
                    continue
                expectedType = attrs[inputParm]['type']
                # A) Check whether given value type is custom type
                if expectedType not in PRIMITIVE_TYPES.keys():
                    status = self._checkCustomType(expectedType,
                                                   inputParm,
                                                   inputVal)
                    if not status[0]:
                        return status
                    else:
                        # contiue to validate remaining given attributes
                        continue
                # B) General type attributes
                # Check the given value type is valid and
                # its matched with the required type defined in yaml
                if not PRIMITIVE_TYPES[expectedType](inputVal):
                    return (False, "Invalid parameter type: "
                            + "%s. Expected value type is: %s" % (
                                inputParm, expectedType))
        return(True, "")
