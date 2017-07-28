import maps


class NameSpace(object):
    def __init__(self, *args, **kwargs):
        self.parameters = maps.NamedDict()
        self.parameters["flow_id"] = "Test_flow_id"

    def get_obj_flow(self, *args, **kwargs):
        return NameSpace

    def get_flow(self, *args, **kwargs):
        return NameSpace

    def run(self):
        pass
