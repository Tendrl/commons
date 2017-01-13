import os
import sys

import ansible.executor.module_common as module_common
from ansible import modules
from mock import MagicMock
import pytest

sys.modules['tendrl.commons.config'] = MagicMock()

from tendrl.commons.utils.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.commons.utils.ansible_module_runner \
    import AnsibleRunner

del sys.modules['tendrl.commons.config']


class TestAnsibleRunnerConstructor(object):
    def test_invalid_module_path(self, monkeypatch):
        pytest.raises(
            ValueError,
            AnsibleRunner,
            "invalid/module/path",
            '/tmp_exec_path',
            key1="value1",
            key2="value2"
        )

    def test_insufficient_arguments(self, monkeypatch):
        pytest.raises(
            ValueError,
            AnsibleRunner,
            "core/commands/command.py"
        )

    def test_successful_ansible_runner(self, monkeypatch):
        runner = AnsibleRunner(
            "core/commands/command.py",
            '/tmp/',
            key1="value1",
            key2="value2",
        )
        assert runner.module_path == modules.__path__[0] + "/" + \
            "core/commands/command.py"
        assert runner.argument_dict == {"key1": "value1",
                                        "key2": "value2"}


class TestAnsibleRunner(object):
    def test_module_executable_generation_failed(self, monkeypatch):
        def mockreturn(path):
            return True

        monkeypatch.setattr(os.path, 'isfile', mockreturn)

        runner = AnsibleRunner(
            "/tmp/testansiblemodulefile",
            '/tmp/',
            key1="value1",
            key2="value2"
        )
        pytest.raises(
            AnsibleExecutableGenerationFailed,
            runner.run
        )

    def test_module_run(self, monkeypatch):
        def mock_modify_module(modname, modpath, argument, task_vars={}):
            return ("echo \'{\"key\":\"test message\"}\'",
                    "new", "#! /usr/bin/sh")

        monkeypatch.setattr(module_common,
                            'modify_module', mock_modify_module)

        def mock_isfile(path):
            return True

        monkeypatch.setattr(os.path, 'isfile', mock_isfile)

        runner = AnsibleRunner(
            "/tmp/testansiblemodulefile",
            "/tmp/",
            key1="value1",
            key2="value2"
        )

        out, err = runner.run()
        assert out == {"key": "test message"}
        assert err == ""
