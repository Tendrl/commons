import abc
import six

from tendrl.common.atoms.exceptions import AtomNotImplementedError


@six.add_metaclass(abc.ABCMeta)
class BaseAtom(object):
    def __init__(
        self,
        name,
        enabled,
        help,
        inputs,
        outputs,
        uuid
    ):
        self.name = name
        self.enabled = enabled
        self.inputs = inputs
        self.help = help
        self.outputs = outputs
        self.uuid = uuid

    @abc.abstractmethod
    def run(self, parameters):
        raise AtomNotImplementedError(
            'define the function run to use this class'
        )
