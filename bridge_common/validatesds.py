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
                   'Long': lambda value: isinstance(value, (six.integer_types, float)),
                   'String': lambda value: isinstance(value, six.string_types),
                   'Uint': lambda value: isinstance(value, int) and value >= 0,
                   'list': lambda value: isinstance(value, list)}


class SchemaNotFound(Exception):
    pass


def locateSchema(schemaName='operations'):
    """
    Locate the bridge operation schema file whether we are running
    from within the source dir or from installed location
    """
    localpath = os.path.dirname(__file__)
    installedpath = "/usr/local/share/tendrl/"
    for directory in (localpath, installedpath):
        path = os.path.join(directory, "sds_state_" + schemaName + '.yaml')
        # we use source tree and deployment directory
        # so we need to check whether file exists
        if os.path.exists(path):
            return path

        raise SchemaNotFound("Unable to find API schema file in %s or %s",
                             localpath, installedpath)

    
def loadSchema(schemaName):
    schemaFile = locateSchema(schemaName)
    try:
        # Check api operation schema file exists
        if not os.path.isfile(schemaFile):
            return (False, "Error: Schema file '"+ schemaFile + "' does not exists.")
            
        # load api operation schema file and return
	try:
	    code = open(schemaFile)
        except IOError, exc:
            return (return_status, "Error loading schema file '"+ schemaFile + "': " + exc)

        # Parse schema file
        try:
            config = yaml.load(code)
        except yaml.YAMLError, exc:
            error_pos = ""
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                error_pos = " at position: (%s:%s)" % (exc.problem_mark.line+1,
                                                       exc.problem_mark.column+1)
            return (False, "Error loading schema file '"+ SchemaFile + "'" + error_pos \
                    + ": content format error: Failed to parse yaml format")

    except Exception, e:
        return (False, "Error loading api operation schema file '" \
                + schemaFile + "': " + str(e))
                
    return (True, config)


def validateApiWithYamlConf(apiJob, yamlConf):
    if yamlConf.has_key('valid_objects'):
        if apiJob['object_type'] not in yamlConf['valid_objects']:
	    return (False, "Invalid object type or object type not supported!")

    # Check flow exists
    if apiJob['flow'] not in yamlConf['object_details'][apiJob['object_type']]['atoms']:
	return (False, "Invalid flow type or flow not supported!")

    # check whether given api-job has any arguments to check
    # or any arguments defined for this purticular job in the yaml.
    atom = yamlConf['object_details'][apiJob['object_type']]['atoms'][apiJob['flow']]
    if not atom.has_key('local_inputs') or not apiJob.has_key('attributes'):
        return (True, "")

    # check whether any required argument is missing.
    # check the list of arguments given by api-job with the
    # list of required argument mentioned under flow tag in the yaml config.
    missingInputParm = set(atom['local_inputs']).difference(
        set(apiJob['attributes'].keys()))
    if missingInputParm != set():
        return (False, "Missing input argument(s) %s" % (list(missingInputParm)))

    # check whether all the given arguments are defined in the yaml file.
    missingConfigParm = set(atom['local_inputs']).difference(
        set(apiJob['attributes'].keys()))
    if missingInputParm != set():
        return (False, "Input argument(s) not defined in yaml file: %s" % (
            list(missingConfigParm)))

    # verify whether argument value align with required type.
    # collect the attribute name and its type and check with the
    # type mentioned in the yaml file for the variable name.  
    attrs = yamlConf['object_details'][apiJob['object_type']]['attrs']
    for inputParm, inputVal in apiJob['attributes'].items():
        # Some arguments does not required any purticular type. ex:- force, enable
        # Contine validating next parm if the type not defined in yaml.
        if not attrs.has_key(inputParm):
            continue
        if not attrs[inputParm]['type'] in PRIMITIVE_TYPES.keys():
            return (False, "Invalid parameter type :%s or " \
                    + "parameter type not supported" % attrs[inputParm]['type'])
        # Check the given value type and the required type is matching
        if not PRIMITIVE_TYPES[attrs[inputParm]['type']](inputVal):
            return (False, "Invalid parameter type: %s. " \
                    + "Expected value type is: %s" % (inputParm, attrs[inputParm]['type']))
    return(True, "")
    

class SdsOperations(object):
    def __init__(self):
        # load the schema into memory to avoid frequent loading
        _, self.nodeYaml = loadSchema('node')
        _, self.cephYaml = loadSchema('ceph')
        _, self.glusterYaml = loadSchema('gluster')
        _, self.bridgeYaml = loadSchema('common')

    def getSchema(self, schemaName):
        if schemaName == 'node':
            return self.nodeYaml
        elif schemaName == 'ceph':
            return self.cephYaml
        elif schemaName == 'gluster':
            return self.glusterYaml
        elif schemaName == 'common':
            return self.bridgeYaml
        else:
            return None

    def validateApi(self, apiJob):
        # Check object type exists
        if isinstance(apiJob, dict) and not apiJob.has_key('object_type'):
            return (False, "Invalid request. Object type not found")

        if not apiJob.has_key('flow'):
            return (False, "Invalid request. Flow name not found")

        schema = self.getSchema(apiJob['sds_type'])
        if not schema:
            return (False, "API Operation Schema file not found " \
                    + "for the sds type:%s" % apiJob['sds_type'])

        return validateApiWithYamlConf(apiJob, schema)
