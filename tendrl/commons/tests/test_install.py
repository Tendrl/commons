import sys

import pytest
from mock import MagicMock

sys.modules['tendrl.commons.config'] = MagicMock()

from tendrl.commons.utils.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.commons.utils.ansible_module_runner \
    import AnsibleRunner
from tendrl.commons.utils.package_installer \
    import Installer

del sys.modules['tendrl.commons.config']


class TestInstaller(object):
    def test_installer_constructor(self, monkeypatch):
        installer = Installer("emacs", "rpm", "2.3.3")
        expected_attr = {"name": "emacs-2.3.3"}
        expecter_module_path = "core/packaging/os/yum.py"

        assert expected_attr == installer.attributes
        assert expecter_module_path == installer.ansible_module_path

        installer = Installer("emacs", "pip")
        expected_attr = {"name": "emacs",
                         "editable": "false"}
        expecter_module_path = "core/packaging/language/pip.py"

        assert expected_attr == installer.attributes
        assert expecter_module_path == installer.ansible_module_path

    def test_installer_constructor_exception(self, monkeypatch):
        pytest.raises(
            ValueError,
            Installer,
            "emacs",
            "exe"
        )

    def test_installer_error(self, monkeypatch):
        def mock_runner_run(obj):
            raise AnsibleExecutableGenerationFailed(
                "module_path", "arg",
                "err message"
            )

        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        installer = Installer("emacs", "rpm", "3.4.5")
        message, success = installer.install()

        assert not success
        assert message == "Executabe could not be generated for module" \
                          " module_path , with arguments arg. Error: err " \
                          "message"

    def test_installer(self, monkeypatch):
        def mock_runner_run(obj):
            result = {
                u'msg': u'',
                u'invocation': {
                    u'module_args': {
                        u'name': [u'elinks'],
                        u'list': None,
                        u'disable_gpg_check': False,
                        u'conf_file': None,
                        u'install_repoquery': True,
                        u'state': u'installed',
                        u'disablerepo': None,
                        u'update_cache': False,
                        u'enablerepo': None,
                        u'exclude': None,
                        u'validate_certs': True
                    }
                },
                u'changed': False,
                u'results': [
                    u'elinks-0.12-0.36.pre6.el7.x86_64 providing '
                    'elinks is already installed'],
                u'rc': 0
            }
            return result, ""

        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        installer = Installer("emacs", "rpm", "3.4.5")
        message, success = installer.install()

        assert message == ""
        assert success
