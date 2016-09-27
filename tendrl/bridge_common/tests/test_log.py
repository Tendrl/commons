from mock import MagicMock
import sys
sys.modules['tendrl.bridge_common.config'] = MagicMock()
from tendrl.bridge_common import log


class Test_log(object):
    def test_log(self):
        assert log.root is not None
        log.root.setLevel.assert_called()
