class AtomNotImplementedError(NotImplementedError):
    def __init___(self, err):
        self.message = "run function not implemented. %s".format(err)


class AtomExecutionFailedError(Exception):
    def __init___(self, err):
        self.message = "Atom Execution failed. Error:" + \
                       " %s".format(err)
