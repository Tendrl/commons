from mock import MagicMock
import pytest
import sys
sys.modules['tendrl.commons.config'] = MagicMock()

from tendrl.commons.utils.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.commons.utils.ansible_module_runner \
    import AnsibleRunner
from tendrl.commons.utils.command \
    import Command
from tendrl.commons.utils.command \
    import UnsupportedCommandException

del sys.modules['tendrl.commons.config']


class TestCommand(object):
    def test_command_run(self, monkeypatch):

        def mock_runner_run(obj):
            result = {
                u'changed': True,
                u'end': u'2016-12-15 17:04:18.558080',
                u'stdout': u'Hello world',
                u'cmd': [u'cat /asdf.txt'],
                u'start': u'2016-12-15 17:04:18.552893',
                u'delta': u'0:00:00.005187', u'stderr': u'', u'rc': 0,
                u'invocation': {
                    u'module_args': {
                        u'creates': None,
                        u'executable': None,
                        u'chdir': None,
                        u'_raw_params': u'pwd',
                        u'removes': None,
                        u'warn': True,
                        u'_uses_shell': False
                    }
                },
                u'warnings': []
            }
            return result, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        c = Command("cat /asdf.txt")
        stdout, stderr, rc = c.run()

        assert stdout == "Hello world"
        assert stderr == ""
        assert rc == 0

    def test_command_error(self, monkeypatch):

        def mock_runner_run(obj):
            raise AnsibleExecutableGenerationFailed(
                "module_path", "arg",
                "err message"
            )
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        c = Command("cat /asdf")
        stdout, stderr, rc = c.run()

        assert stdout == ""
        assert stderr == "Executabe could not be generated for module" \
            " module_path , with arguments arg. Error: err message"
        assert rc == -1

    def test_command_unsafe_command(self, monkeypatch):
        pytest.raises(
            UnsupportedCommandException,
            Command,
            "rm -f /sadf"
        )
