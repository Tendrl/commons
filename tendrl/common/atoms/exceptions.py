class AtomNotImplementedError(NotImplementedError):
    def __init___(self, err):
        self.message = "run function not implemented. %s".format(err)
