from tendrl.common.utils.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.common.utils.ansible_module_runner \
    import AnsibleRunner
from tendrl.common.utils.command \
    import Command


class TestCommand(object):
    def test_command_run(self, monkeypatch):

        def mock_runner_run(obj):
            return {"message": "test_message"}, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        c = Command("echo test_message")
        result, err = c.run()

        assert result == {"message": "test_message"}
        assert err == ""

    def test_command_error(self, monkeypatch):

        def mock_runner_run(obj):
            raise AnsibleExecutableGenerationFailed(
                "module_path", "arg",
                "err message"
            )
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        c = Command("echo hello_world")
        result, err = c.run()

        assert result == {}
        assert err == "Executabe could not be generated for module" \
            " module_path , with arguments arg. Error: err message"
