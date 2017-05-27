import pytest
import __builtin__
from tendrl.commons.utils.ansible_module_runner import AnsibleExecutableGenerationFailed
from tendrl.commons.utils.ansible_module_runner import AnsibleModuleNotFound
from tendrl.commons.utils.ansible_module_runner import AnsibleRunner
from mock import patch
import mock
import maps
import os
import ansible.executor.module_common as module_common
import importlib
import sys
from mock import MagicMock

def system(*args):
    raise ValueError("Testing Error")

def test_AnsibleExecutableGenerationFailed_constructor():
    ansible_obj = AnsibleExecutableGenerationFailed()
    assert ansible_obj.message == "Executabe could not be generated for module" \
                       " None . Error: None"
    ansible_obj = AnsibleExecutableGenerationFailed(module_path="Test\path",
                                                    arguments="temp_args",
                                                    err="No Error")
    assert ansible_obj.message== "Executabe could not be generated for module" \
                       " Test\path . Error: No Error"


def test_AnsibleModuleNotFound_constructor():
    ansible_obj = AnsibleModuleNotFound()
    assert ansible_obj.message == "Ansible module None not found"
    ansible_obj = AnsibleModuleNotFound(module_path="Test\path")
    assert ansible_obj.message== "Ansible module Test\path not found"


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_AnsibleRunner_constructor():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id =1
    with patch.object(os.path,'isfile',return_value = False) as mock_isfile:
        with pytest.raises(AnsibleModuleNotFound):
            ansible_obj = AnsibleRunner("Test_module")
    with patch.object(os.path,'isfile',return_value = True) as mock_isfile:
        with pytest.raises(ValueError):
            ansible_obj = AnsibleRunner("Test_module")
        ansible_obj = AnsibleRunner("Test_module",ansible="test_ansible")
        assert "_ansible_selinux_special_fs" in ansible_obj.argument_dict.keys()


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id =1
    with patch.object(os.path,'isfile',return_value = True) as mock_isfile:
        ansible_obj = AnsibleRunner("path\\to\\test\\module",ansible="test_ansible")
        with pytest.raises(AnsibleExecutableGenerationFailed):
            ansible_obj.run()
        with patch.object(module_common,'modify_module') as mock_modify_module:
            mock_modify_module.return_value = "Module_data","module_style","shebang"
            ansible_obj.run()
        with patch.object(module_common,'modify_module') as mock_modify_module:
            with patch.object(os,"system",system) as mock_system:
                mock_modify_module.return_value = "Module_data","module_style","shebang"
                ansible_obj.run()

def test_module():
    sys.modules['json'] =  "jsons"
    module = importlib.import_module("tendrl.commons.utils.ansible_module_runner")

