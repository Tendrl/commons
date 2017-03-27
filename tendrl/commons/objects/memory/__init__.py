from tendrl.commons.event import Event
from tendrl.commons import etcdobj
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.utils import cmd_utils

from tendrl.commons import objects


class Memory(objects.BaseObject):
    def __init__(self, total_size=None, swap_total=None,
                 *args, **kwargs):
        super(Memory, self).__init__(*args, **kwargs)
        memory = self._getNodeMemory()
        self.value = 'nodes/%s/Memory'
        self.total_size = total_size or memory["TotalSize"]
        self.swap_total = swap_total or memory["SwapTotal"]
        self._etcd_cls = _MemoryEtcd

    def _getNodeMemory(self):
        '''returns structure

        {"nodename": [{"TotalSize": "totalsize",

                   "SwapTotal": "swaptotal",

                   "Type":      "type"}, ...], ...}

        '''
        try:
            out = None
            with open('/proc/meminfo') as f:
                out = f.read()
        except IOError as ex:
            Event(
                ExceptionMessage(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={"message": "Unable to find memory details",
                             "exception": ex
                             }
                )
            )

        if out:
            info_list = out.split('\n')
            memoinfo = {
                'TotalSize': info_list[0].split(':')[1].strip(),
                'SwapTotal': info_list[14].split(':')[1].strip()
            }
        else:
            memoinfo = {
                'TotalSize': '',
                'SwapTotal': ''
            }

        return memoinfo


class _MemoryEtcd(etcdobj.EtcdObj):
    """A table of the memory, lazily updated

    """
    __name__ = 'nodes/%s/Memory'
    _tendrl_cls = Memory

    def render(self):
        self.__name__ = self.__name__ % NS.node_context.node_id
        return super(_MemoryEtcd, self).render()
