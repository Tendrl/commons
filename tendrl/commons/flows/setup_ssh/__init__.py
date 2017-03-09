# flake8: noqa

from tendrl.commons import flows


class SetupSsh(flows.BaseFlow):
    def run(self):
        prov_node = self.parameters.get("provisioner_node")
        plugin = NS.provisioner.get_plugin()
        plugin.setup(prov_node)

    def load_definition(self):
        return {"help": "Setup SSH",
                "uuid": "dc4c8775-1595-43c7-a6c6-517f0081598f"}