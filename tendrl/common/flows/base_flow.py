import abc
import six

from tendrl.common.flows.exceptions import FlowNotImplementedError


@six.add_metaclass(abc.ABCMeta)
class BaseFlow(object):
    @abc.abstractmethod
    def run(self):
        raise FlowNotImplementedError(
            'define the function run to use this class'
        )
