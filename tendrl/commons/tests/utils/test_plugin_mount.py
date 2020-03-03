import builtins
from mock import patch

from tendrl.commons.utils.plugin_mount import PluginMount


def test_constructor():
    plugin_mount = PluginMount("Test_class", (object,), {})
    assert hasattr(plugin_mount, 'plugins')
    plugin_mount.__init__('Dummy', (object,), {})
    cls_body = dict(__doc__='docstring', __name__='Dummy class',
                    __module__='modname')
    with patch.object(__builtin__, 'hasattr', return_value=True):
        with patch.object(PluginMount, 'register_plugin', return_value=True):
            PluginMount("Test_class", (object,), cls_body)


def test_register_plugin():
    cls_body = dict(__doc__='docstring', __name__='Dummy class',
                    __module__='modname')
    cls = type('Dummy', (object,), cls_body)
    plugin_mount = PluginMount("Test_class", (object,), {})
    plugin_mount.register_plugin(cls)
    assert isinstance(plugin_mount.plugins[0], cls)
