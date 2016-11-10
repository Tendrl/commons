import six


PRIMITIVE_TYPES = {'Boolean': lambda value: isinstance(value, bool),
                   'Float': lambda value: isinstance(value, float),
                   'Integer': lambda value: isinstance(value, int),
                   'Long': lambda value: isinstance(value, (
                       six.integer_types, float)),
                   'String': lambda value: isinstance(value, six.string_types),
                   'Uint': lambda value: isinstance(value, int) and value >= 0,
                   'List': lambda value: isinstance(value, list)}


class JobValidateException(Exception):
    message = "Job validation exception"

    def __init__(self, message='Job validation exception'):
        self.message = message

    def __str__(self):
        return self.message

    def response(self):
        return {'status': {'message': str(self)}}


class DefinitionsSchemaValidatorException(Exception):
    message = "Tendrl Definitions Schema validation exception"

    def __init__(self, message='Tendrl Definitions Schema validation exception'):
        self.message = message

    def __str__(self):
        return self.message

    def response(self):
        return {'status': {'message': str(self)}}


class NoNameSpaceFound(DefinitionsSchemaValidatorException):
    message = "No Tendrl Namespace found in the yaml file"

class FlowDetailsNotFoundException(JobValidateException):
    message = "Flow details not found in the yaml file"

class DefinitionsSchemaValidator(object):
    def __init__(self, definition_yaml):
        self.definitions_yaml = definition_yaml

    def sanitize_definitions(self):
        definitions = dict()
        for namespace, defs in self.definitions_yaml.iteritems():
            if "namespace" in namespace:
                # Extracts "tendrl.<component>..." from the
                # "namespace.tendrl.<component>..." key
                if "objects" not in defs.keys():
                    msg = "No objects found in namespace %s" % namespace
                    raise DefinitionsSchemaValidatorException(msg)
                definitions[".".join(namespace.split(".")[1:])] = defs
        if bool(definitions) == False:
            raise NoNameSpaceFound()
        definitions['tendrl_schema_version'] = self.definitions_yaml[
            'tendrl_schema_version']
        return definitions

class JobValidator(object):
    def __init__(self, definitions_dict):
        self.definitions = definitions_dict
        self.objects = dict()
        for namespace, defs in self.definitions.iteritems():
            namespace = self.definitions[namespace]
            if isinstance(namespace, dict):
                self.objects.update(namespace['objects'])

    def checkFlow(self, flow):
        if self.definitions['tendrl_schema_version'] == 0.3:
            return self.checkFlowV3(flow)

    def checkAtom(self, atom, objects):
        if self.definitions['tendrl_schema_version'] == 0.3:
            return self.checkAtomV3(atom, objects)

    def validateApi(self, job):
        if self.definitions['tendrl_schema_version'] == 0.3:
            return self.validateApiV3(job)

    def checkFlowV3(self, flow):
        # Extract namespace from flow_name
        if not flow:
            return (False,
                    "Flow: %s not defined" %
                    (flow))
        # Check flow enabled
        if flow.get('enabled') is not True:
            return (False,
                    "Flow: %s not enabled" %
                    (flow))
        # Check uuid exists
        if 'uuid' not in flow:
            return (False,
                    "uuid not found for the flow: %s" %
                    (flow))
        # Check atoms exists
        if 'atoms' not in flow:
            return (False,
                    "atoms not found for the flow: %s" %
                    (flow))
        if 'inputs' not in flow:
            return (False,
                    "inputs not found for the flow: %s" %
                    (flow))
        if 'mandatory' not in flow['inputs']:
            return (False,
                    "mandatory field not found in inputs of a flow: %s" %
                    (flow))
        if 'run' not in flow:
            return (False,
                    "run not found for the flow: %s" %
                    (flow))
        elif flow['run'] == "":
            return (False,
                    "no value set for attribute run for the flow: %s" %
                    (flow))
        if 'type' not in flow:
            return (False,
                    "type not found for the flow: %s" %
                    (flow))
        elif flow['type'] == "":
            return (False,
                    "no value set for attribute type for the flow: %s" %
                    (flow))
        return (True, flow)

    def checkAtomV3(self, atom, objects):
        # Get the object
        obj_name, con, atom_name = atom.split('.')[-3:]
        obj = objects.get(obj_name, {})
        if not obj:
            return (False,
                    "object atom details not found for:%s" %
                    (obj_name))
        # get the atom
        atom = obj.get(con, {}).get(atom_name, {})
        # Check whether atoms defined
        if not atom:
            return (False,
                    "atom:%s details not found for:%s" %
                    (atom_name, obj_name))
        if 'uuid' not in atom:
            return (False,
                    "uuid not found for the atom:%s.%s" %
                    (obj_name, atom_name))
        elif atom['uuid'] == "":
            return (False,
                    "no value set for attribute uuid for the atom:%s.%s" %
                    (obj_name, atom_name))
        if 'enabled' not in atom:
            return (False,
                    "enabled not found for the atom:%s.%s" % (obj_name,
                                                              atom_name))
        if 'name' not in atom:
            return (False,
                    "name not found for the atom:%s.%s" %
                    (obj_name, atom_name))
        elif atom['name'] == "":
            return (False,
                    "no value set for attribute name for the atom:%s.%s" %
                    (obj_name, atom_name))
        if 'inputs' not in atom:
            return (False,
                    "inputs not found for the atom:%s.%s" %
                    (obj_name, atom_name))
        # TODO(rohan) fix this mandatory check for flow injected inputs
 #       if 'mandatory' not in atom['inputs']:
 #           return (False,
 #                   "mandatory field not found in inputs of the atom: %s.%s" %
 #                   (obj_name, atom_name))
        if 'run' not in atom:
            return (False,
                    "run not found for the atom:%s.%s" %
                    (obj_name, atom_name))
        elif atom['run'] == "":
            return (False,
                    "no value set for attribute run for the atom:%s.%s" %
                    (obj_name, atom_name))
        if 'type' not in atom:
            return (False,
                    "type not found for the atom:%s.%s" %
                    (obj_name, atom_name))
        elif atom['type'] == "":
            return (False,
                    "no value set for attribute type for the atom:%s.%s" %
                    (obj_name, atom_name))
        return (True, '')

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

    def checkInputType(self, gvnParm, objects):
        # Check the given input parameter's type using
        # the parameters of the object type.
        for parm, val in gvnParm.items():
            # Some arguments does not required any particular type.
            # Contine validating next parm if the type of the
            # inputparm not defined in yaml.
            obj_name, iParm = parm.split(".")

            parms = objects[obj_name]['attrs']
            if iParm not in parms:
                continue
            expectedType = parms[iParm].get('type')
            # A) Check whether given value type is custom type
            if expectedType not in PRIMITIVE_TYPES.keys():
                status = self._checkCustomType(expectedType, iParm, val,
                                               objects)
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

    def getFlowParms(self, flow):
        """This function will return mandatory and

        optional parameters of the given flow from the loaded yaml
        """
        return (flow["inputs"].get("mandatory"), flow["inputs"].get(
            "optional", []))

    def getAtomParms(self, atom, objects):
        """This function will return mandatory and

        optional parameters of the given atom from the loaded yaml
        """
        obj_name, con, atom_name = atom.split('.')[-3:]
        return (objects.get(
            obj_name, {}).get(con, {}).get(atom_name, {}).get(
                "inputs", {}).get("mandatory"),
            objects.get(
                obj_name, {}).get(con, {}).get(atom_name, {}).get(
                    "inputs", {}).get("optional"))

    def _checkCustomType(self, customType, inputParm, inputVal, objects):
        def _check(inputVal, cType=customType):
            # check whether the custom defined type is decleared!
            typeDef = objects.get(cType.lower())
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

    def validateApiV3(self, job):
        if "cluster_id" not in job:
            return (False, "Cluster id not found in the job")
        if "flow" not in job:
            return (False, "flow not found in the job")
        if "parameters" not in job:
            return (False, "input parameters not found in the job")

        namespace = self.definitions[job["flow"].split("flows")[0].strip(".")]
        flow_class_name = job["flow"].split("flows")[-1].strip(".")

        # Get flow from the extracted namespace
        flow = namespace['flows'].get(flow_class_name)
        objects = self.objects

        # Checking flow details!
        status = self.checkFlow(flow)
        if not status[0]:
            return status

        reqParm, optParm = self.getFlowParms(flow)
        # no need to check anything if no parameters are required
        if reqParm:
            # check whether all the required parameters are given
            status = self.checkJobRequiredParm(job["parameters"], reqParm)
            if not status[0]:
                return status
            # check whether all the parameters are defined in yaml
            status = self.checkJobParmDefined(job["parameters"],
                                              reqParm + optParm)
            if not status[0]:
                return status
            # check given parameters type
            inputParmWithObj = self.getParmPath(job["parameters"],
                                                reqParm + optParm)
            status = self.checkInputType(inputParmWithObj, objects)
            if not status[0]:
                return status

        # Checking atoms of the flow
        atoms = flow.get('atoms', {})
        if not atoms:
            return (False,
                    "flow:%d does not have any atom defined" % job["flow"])
        for atom in atoms:
            status = self.checkAtom(atom, objects)
            if not status[0]:
                return status
            reqParm, optParm = self.getAtomParms(atom, objects)
            if not reqParm:
                return (True, '')
            # check whether all the required parameters are given
            status = self.checkJobRequiredParm(job["parameters"], reqParm)
            if not status[0]:
                return status
            # check whether all the parameters are defined in yaml
            status = self.checkJobParmDefined(job["parameters"],
                                              reqParm + optParm)
            if not status[0]:
                return status
            # check given parameters type
            inputParmWithObj = self.getParmPath(job["parameters"],
                                                reqParm + optParm)
            status = self.checkInputType(inputParmWithObj, objects)
            if not status[0]:
                return status
        # all check passed successfully!
        return(True, '')
