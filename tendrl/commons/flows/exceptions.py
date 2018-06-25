class FlowNotImplementedError(NotImplementedError):
    def __init___(self, err):
        self.message = "run function not implemented. %s".format(err)


class FlowExecutionFailedError(Exception):
    def __init___(self, err):
        self.message = "Flow Execution failed. Error:" + \
                       " %s".format(err)