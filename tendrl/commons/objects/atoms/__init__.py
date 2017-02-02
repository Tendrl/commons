import abc

import six


@six.add_metaclass(abc.ABCMeta)
class BaseAtom(object):
    def __init__(
            self,
            inputs=None,
            enabled=None,
            outputs=None,
            uuid=None,
            parameters=None,
            help=None
    ):

        obj_def = tendrl_ns.definitions.get_obj_definition(tendrl_ns.to_str,
                                             self.obj.__name__)
        atom_def = obj_def.atoms[self.__class__.__name__]

        self.inputs = inputs or atom_def.get('inputs').get('mandatory')
        self.enabled = enabled or atom_def.get('enabled')
        self.outputs = outputs or atom_def.get('outputs')
        self.uuid = uuid or atom_def.get('uuid')
        self.help = help or atom_def.get('help')
        self.parameters = parameters

    @abc.abstractmethod
    def run(self):
        raise AtomNotImplementedError(
            'define the function run to use this class'
        )

    def __new__(cls, *args, **kwargs):

        super_new = super(BaseAtom, cls).__new__
        if super_new is object.__new__:
            instance = super_new(cls)
        else:
            instance = super_new(cls, *args, **kwargs)

        return instance


class AtomNotImplementedError(NotImplementedError):
    def __init___(self, err):
        self.message = "run function not implemented. %s".format(err)


class AtomExecutionFailedError(Exception):
    def __init___(self, err):
        self.message = "Atom Execution failed. Error:" + \
                       " %s".format(err)
