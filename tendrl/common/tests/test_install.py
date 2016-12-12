import pytest
from tendrl.common.utils.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.common.utils.ansible_module_runner \
    import AnsibleRunner
from tendrl.common.utils.install \
    import Installer


class Test_installer(object):
    def test_installer_constructor(self, monkeypatch):
        installer = Installer("emacs", "yum", "2.3.3")
        expected_attr = {"name": "emacs",
                         "version": "2.3.3"}
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

        installer = Installer("emacs", "yum", "3.4.5")
        result, err = installer.install()

        assert result == {}
        assert err == "Executabe could not be generated for module" \
            " module_path , with arguments arg. Error: err message"

    def test_installer(self, monkeypatch):

        def mock_runner_run(obj):
            return {"message": "installed package successfully"}, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        installer = Installer("emacs", "yum", "3.4.5")
        result, err = installer.install()

        assert result == {"message": "installed package successfully"}
        assert err == ""
