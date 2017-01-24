import abc
import logging

import six

from tendrl.commons.objects.atoms import AtomExecutionFailedError
from tendrl.commons.flows import utils as flow_utils

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseFlow(object):
    def __init__(
            self,
            atoms=None,
            help=None,
            enabled=None,
            inputs=None,
            pre_run=None,
            post_run=None,
            type=None,
            uuid=None,
            parameters=None,
            request_id=None
    ):
        if hasattr(self, "obj"):
            # flow_fqn eg:tendrl.node_agent.objects.abc.flows.temp_flows
            obj_name = self.obj.__name__
            obj_def = tendrl_ns.definitions.get_obj_definition(
                tendrl_ns.to_str,
                obj_name)
            flow_def = obj_def.flows[self.__class__.__name__]
            self.to_str = "%s.objects.%s.flows.%s" % (tendrl_ns.to_str,
                                                      obj_name,
                                                      self.__class__.__name__)
        else:
            # flow_fqn eg: tendrl.node_agent.flows.temp_flows
            flow_def = tendrl_ns.definitions.get_flow_definition(
                tendrl_ns.to_str, self.__class__.__name__)
            self.to_str = "%s.flows.%s" % (tendrl_ns.to_str,
                                           self.__class__.__name__)


        self.atoms = atoms or flow_def['atoms']
        self.help = help or flow_def['help']
        self.enabled = enabled or flow_def['enabled']
        self.inputs = inputs or flow_def['inputs']
        self.pre_run = pre_run or flow_def['pre_run']
        self.post_run = post_run or flow_def['post_run']
        self.type = type or flow_def['type']
        self.uuid = uuid or flow_def['uuid']
        self.parameters = parameters
        self.request_id = request_id
        self.parameters.update({'request_id': self.request_id})

        # Flows and atoms expected to APPEND their job statuses to appropriate
        # log levels list below, logging everything to "all" is mandatory
        self.log = {"all": [], "info": [], "error": [], "warn": [],
                    "debug": []}


    @abc.abstractmethod
    def run(self):
        # Execute the pre runs for the flow
        msg = "Processing pre-runs for flow: %s" % self.to_str
        LOG.info(msg)
        flow_utils.update_job_status(self.request_id, msg, self.log,
                                     'info', tendrl_ns.etcd_orm)

        if self.pre_run is not None:
            for atom_fqn in self.pre_run:
                msg = "Start pre-run : %s" % atom_fqn
                LOG.info(msg)
                self.log['all'].append(msg)
                self.log['info'].append(msg)

                ret_val = self.execute_atom(atom_fqn)

                if not ret_val:
                    msg = "Failed pre-run: %s for flow: %s" % \
                          (atom_fqn, self.job['run'])
                    LOG.error(msg)
                    flow_utils.update_job_status(self.request_id, msg,
                                                 self.log,
                                                 'error', self.etcd_orm)

                    raise AtomExecutionFailedError(
                        "Error executing pre run function: %s for flow: %s" %
                        (atom_fqn, self.job['run'])
                    )
                else:
                    msg = "Finished pre-run: %s for flow: %s" %\
                          (atom_fqn, self.job['run'])
                    LOG.info(msg)
                    self.log['all'].append(msg)
                    self.log['info'].append(msg)

        # Execute the atoms for the flow
        msg = "Processing atoms for flow: %s" % self.job['run']
        LOG.info(msg)
        flow_utils.update_job_status(self.request_id, msg, self.log,
                                     'info', self.etcd_orm)

        for atom_fqn in self.atoms:
            msg = "Start atom : %s" % atom_fqn
            LOG.info(msg)
            self.log['all'].append(msg)
            self.log['info'].append(msg)

            ret_val = self.execute_atom(atom_fqn)

            if not ret_val:
                msg = "Failed atom: %s on flow: %s" % \
                      (atom_fqn, self.job['run'])
                LOG.error(msg)
                flow_utils.update_job_status(self.request_id, msg, self.log,
                                             'error', self.etcd_orm)

                raise AtomExecutionFailedError(
                    "Error executing atom: %s on flow: %s" %
                    (atom_fqn, self.job['run'])
                )
            else:
                msg = 'Finished atom %s for flow: %s' %\
                      (atom_fqn, self.job['run'])
                LOG.info(msg)
                self.log['all'].append(msg)
                self.log['info'].append(msg)

        # Execute the post runs for the flow
        msg = "Processing post-runs for flow: %s" % self.job['run']
        LOG.info(msg)
        flow_utils.update_job_status(self.request_id, msg, self.log,
                                     'info', self.etcd_orm)
        if self.post_run is not None:
            for atom_fqn in self.post_run:
                msg = "Start post-run : %s" % atom_fqn
                LOG.info(msg)
                self.log['all'].append(msg)
                self.log['info'].append(msg)

                ret_val = self.execute_atom(atom_fqn)

                if not ret_val:
                    msg = "Failed post-run: %s for flow: %s" % \
                          (atom_fqn, self.job['run'])
                    LOG.error(msg)
                    flow_utils.update_job_status(self.request_id, msg,
                                                 self.log,
                                                 'error', self.etcd_orm)

                    raise AtomExecutionFailedError(
                        "Error executing post run function: %s" % atom_fqn
                    )
                else:
                    msg = "Finished post-run: %s for flow: %s" %\
                          (atom_fqn, self.job['run'])
                    LOG.info(msg)
                    flow_utils.update_job_status(self.request_id, msg,
                                                 self.log,
                                                 'info', self.etcd_orm)

    def execute_atom(self, atom_fqn):
        # atom_fqn eg: tendrl.node_agent.objects.abc.atoms.xyz

        if "tendrl" in atom_fqn and "atoms" in atom_fqn:
            obj_name, atom_name = atom_fqn.split(".objects.")[-1].split(
                ".atoms.")
            atom = tendrl_ns.get_atom(obj_name, atom_name)
            try:
                ret_val = atom(
                    parameters=self.parameters
                ).run()
            except AtomExecutionFailedError:
                return False

            return ret_val
        return False
