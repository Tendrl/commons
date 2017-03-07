import abc
import logging

import six

from tendrl.commons.objects import AtomExecutionFailedError


LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseFlow(object):
    def __init__(self, parameters=None, request_id=None):

        self.load_definition()
        self.parameters = parameters
        self.request_id = request_id
        self.parameters.update({'request_id': self.request_id})

        # Flows and atoms expected to APPEND their job statuses to appropriate
        # log levels list below, logging everything to "all" is mandatory
        self.log = {"all": [], "info": [], "error": [], "warn": [],
                    "debug": []}

    def load_definition(self):
        obj_name = self.obj.__name__
        cls_name = self.__class__.__name__
        if hasattr(self, "obj"):
            self.definition = self._ns.get_obj_flow_definition(obj_name,
                                                              cls_name)
            self.to_str = "%s.objects.%s.flows.%s" % (self._ns.ns_name,
                                                      obj_name,
                                                      cls_name)
        else:
            self.definition = self._ns.get_flow_definition(cls_name)
            self.to_str = "%s.flows.%s" % (self._ns.ns_name, cls_name)

    @abc.abstractmethod
    def run(self):
        # Execute the pre runs for the flow
        msg = "Processing pre-runs for flow: %s" % self.to_str
        LOG.info(msg)

        if self.pre_run is not None:
            for atom_fqn in self.pre_run:
                msg = "Start pre-run : %s" % atom_fqn
                LOG.info(msg)
                self.log['all'].append(msg)
                self.log['info'].append(msg)

                ret_val = self._execute_atom(atom_fqn)

                if not ret_val:
                    msg = "Failed pre-run: %s for flow: %s" % \
                          (atom_fqn, self.help)
                    LOG.error(msg)
                    raise AtomExecutionFailedError(
                        "Error executing pre run function: %s for flow: %s" %
                        (atom_fqn, self.help)
                    )
                else:
                    msg = "Finished pre-run: %s for flow: %s" %\
                          (atom_fqn, self.help)
                    LOG.info(msg)
                    self.log['all'].append(msg)
                    self.log['info'].append(msg)

        # Execute the atoms for the flow
        msg = "Processing atoms for flow: %s" % self.help
        LOG.info(msg)

        for atom_fqn in self.atoms:
            msg = "Start atom : %s" % atom_fqn
            LOG.info(msg)
            self.log['all'].append(msg)
            self.log['info'].append(msg)

            ret_val = self._execute_atom(atom_fqn)

            if not ret_val:
                msg = "Failed atom: %s on flow: %s" % \
                      (atom_fqn, self.help)
                LOG.error(msg)

                raise AtomExecutionFailedError(
                    "Error executing atom: %s on flow: %s" %
                    (atom_fqn, self.help)
                )
            else:
                msg = 'Finished atom %s for flow: %s' %\
                      (atom_fqn, self.help)
                LOG.info(msg)
                self.log['all'].append(msg)
                self.log['info'].append(msg)

        # Execute the post runs for the flow
        msg = "Processing post-runs for flow: %s" % self.help
        LOG.info(msg)
        if self.post_run is not None:
            for atom_fqn in self.post_run:
                msg = "Start post-run : %s" % atom_fqn
                LOG.info(msg)
                self.log['all'].append(msg)
                self.log['info'].append(msg)

                ret_val = self._execute_atom(atom_fqn)

                if not ret_val:
                    msg = "Failed post-run: %s for flow: %s" % \
                          (atom_fqn, self.help)
                    LOG.error(msg)
                    raise AtomExecutionFailedError(
                        "Error executing post run function: %s" % atom_fqn
                    )
                else:
                    msg = "Finished post-run: %s for flow: %s" %\
                          (atom_fqn, self.help)
                    LOG.info(msg)

    def _execute_atom(self, atom_fqdn):
        try:
            ns, atom_name = atom_fqdn.split(".atoms.")
            ns, obj_name = ns.split(".objects.")

            runnable_atom = self._ns.get_atom(obj_name, atom_name)
            try:
                ret_val = runnable_atom(
                    parameters=self.parameters
                ).run()
                return ret_val
            except AtomExecutionFailedError:
                return False

        except (KeyError, AttributeError) as ex:
            LOG.error(ex)

        return False
