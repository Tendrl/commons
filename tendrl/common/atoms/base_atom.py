import abc


class BaseAtom(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self, parameters):
        raise NotImplementedError(
            'define the function run to use this class'
        )
