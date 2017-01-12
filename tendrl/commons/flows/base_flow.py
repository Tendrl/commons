import abc
import logging

import six

from tendrl.commons.atoms.exceptions import AtomExecutionFailedError
from tendrl.commons.utils import import_utils

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseFlow(object):
    def __init__(
            self,
            name,
            atoms,
            help,
            enabled,
            inputs,
            pre_run,
            post_run,
            type,
            uuid,
            parameters,
            job,
            definitions
    ):
        self.name = name
        self.atoms = atoms
        self.help = help
        self.enabled = enabled
        self.inputs = inputs
        self.pre_run = pre_run
        self.post_run = post_run
        self.type = type
        self.uuid = uuid
        self.parameters = parameters
        self.job = job
        self.definitions = definitions

        # Add etcd_client to parameters via child flows
        self.parameters.update({'log': []})

    @abc.abstractmethod
    def run(self):
        # Execute the pre runs for the flow
        LOG.info("Starting execution of pre-runs for flow: %s" %
                 self.job['run'])
        if self.pre_run is not None:
            for mod in self.pre_run:
                ret_val = self.execute_atom(mod)

                if not ret_val:
                    LOG.error("Failed executing pre-run: %s for flow: %s" %
                              (mod, self.job['run']))
                    raise AtomExecutionFailedError(
                        "Error executing pre run function: %s for flow: %s" %
                        (mod, self.job['run'])
                    )
                else:
                    LOG.info("Successfully executed pre-run: %s for flow: %s" %
                             (mod, self.job['run']))

        # Execute the atoms for the flow
        LOG.info("Starting execution of atoms for flow: %s" %
                 self.job['run'])
        for atom in self.atoms:
            ret_val = self.execute_atom(atom)

            if not ret_val:
                LOG.error("Failed executing atom: %s on flow: %s" %
                          (atom, self.job['run']))
                raise AtomExecutionFailedError(
                    "Error executing atom: %s on flow: %s" %
                    (atom, self.job['run'])
                )
            else:
                LOG.info('Successfully executed atoms for flow: %s' %
                         self.job['run'])

        # Execute the post runs for the flow
        LOG.info("Starting execution of post-runs for flow: %s" %
                 self.job['run'])
        if self.post_run is not None:
            for mod in self.post_run:
                ret_val = self.execute_atom(mod)

                if not ret_val:
                    LOG.error("Failed executing post-run: %s for flow: %s" %
                              (mod, self.job['run']))
                    raise AtomExecutionFailedError(
                        "Error executing post run function: %s" % mod
                    )
                else:
                    LOG.info(
                        "Successfully executed post-run: %s for flow: %s" %
                        (mod, self.job['run'])
                    )

    def extract_atom_details(self, atom_name):
        namespace = atom_name.split('.objects.')[0]
        object_name = atom_name.split('.objects.')[1].split('.atoms.')[0]
        atoms = self.definitions[namespace]['objects'][object_name]['atoms']
        atom = atoms[atom_name.split('.')[-1]]
        return atom.get('name'), atom.get('enabled'), atom.get('help'), \
            atom.get('inputs'), atom.get('outputs'), atom.get('uuid')

    # Executes a givem atom specific by given full module name "mod"
    # It dynamically imports the atom class from module as the_atom
    # and executes the function run() on the instance of same
    def execute_atom(self, mod):
        if "tendrl" in mod and "atoms" in mod:
            atom_name, enabled, help, inputs, outputs, uuid = \
                self.extract_atom_details(mod)
            the_atom = import_utils.load_abs_class(mod)
            try:
                ret_val = the_atom(
                    atom_name,
                    enabled,
                    help,
                    inputs,
                    outputs,
                    uuid
                ).run(self.parameters)
            except AtomExecutionFailedError:
                return False

            return ret_val
        return False
