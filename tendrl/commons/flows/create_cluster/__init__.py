from tendrl.commons import flows


class CreateCluster(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(CreateCluster, self).__init__(*args, **kwargs)

    def run(self):
        super(CreateCluster, self).run()
