import six

from tendrl.commons.atoms.exceptions import AtomNotImplementedError


@six.add_metaclass(abc.ABCMeta)
class BaseAtom(object):
    def __init__(
            self,
            inputs=None,
            enabled=None,
            outputs=None,
            uuid=None,
            parameters=None,
            obj=None,
            help=None
    ):

        obj_def = tendrl_ns.definitions.get_obj_defs(tendrl_ns.to_str,
                                             obj.__class__.__name__)
        atom_def = obj_def.atoms[self.__class__.__name__]

        self.inputs = inputs or atom_def['inputs']['mandatory']
        self.enabled = enabled or atom_def['enabled']
        self.outputs = outputs or atom_def['outputs']
        self.uuid = uuid or atom_def['uuid']
        self.help = help or atom_def['help']
        self.paramaters = parameters

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
