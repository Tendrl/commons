import __builtin__
import maps


from tendrl.commons.objects.platform import Platform


# Testing __init__
def test_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    platform = Platform()
    assert platform is not None
    assert platform.os is None
    platform = Platform(os="Centos", os_version=1.1,
                        kernel_version=2.1)
    assert platform.os == "Centos"


# Testing render
def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    platform = Platform()
    assert platform.render() is not None
