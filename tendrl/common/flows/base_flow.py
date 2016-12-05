import abc


class BaseFlow(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError(
            'define the function run to use this class'
        )
