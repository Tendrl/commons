import psutil


from tendrl.commons import objects


class Memory(objects.BaseObject):
    def __init__(self, memory_total=None, memory_available=None,
                 memory_util_percent=None, swap_total=None,
                 swap_available=None, swap_util_percent=None,
                 *args, **kwargs):
        super(Memory, self).__init__(*args, **kwargs)
        mem = psutil.virtual_memory()
        self.memory_total = memory_total or str(mem.total)
        self.memory_available = memory_available or str(mem.available)
        self.memory_util_percent = memory_util_percent or str(mem.percent)
        swap = psutil.swap_memory()
        self.swap_total = swap_total or str(swap.total)
        self.swap_available = swap_available or str(swap.free)
        self.swap_util_percent = swap_util_percent or str(swap.percent)
        self.value = 'nodes/{0}/Memory'

    def render(self):
        self.value = self.value.format(NS.node_context.node_id)
        return super(Memory, self).render()
