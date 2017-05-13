
from tendrl.commons import objects


class Platform(objects.BaseObject):
    def __init__(self, os=None, os_version=None,
                 kernel_version=None,
                 *args, **kwargs):
        super(Platform, self).__init__(*args, **kwargs)
        self.kernel_version = kernel_version
        self.os = os
        self.os_version = os_version
        self.value = 'nodes/{0}/Platform'

    def render(self):
        self.value = self.value.format(NS.node_context.node_id)
        return super(Platform, self).render()
