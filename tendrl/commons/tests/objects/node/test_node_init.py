import builtins
import maps


from tendrl.commons.objects.node import Node


# Testing __init__
def test_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    node = Node()
    assert node.status is None

    # Passing Dummy Values
    node = Node(fqdn="node/test", status="Failed")
    assert node.status == "Failed"


# Testing render
def test_render():
    setattr(builtins, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    node = Node()
    assert node.render() is not None
