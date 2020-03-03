import builtins
import maps
import mock

from tendrl.commons.utils import log_utils


def test_log():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    with mock.patch('tendrl.commons.event.Event.__init__',
                    mock.Mock(return_value=None)):
        with mock.patch('tendrl.commons.message.Message.__init__',
                        mock.Mock(return_value=None)):
            log_utils.log("info", "node_context", {"message": "test"})
    log_utils.log("error", None, {"message": "test"})
