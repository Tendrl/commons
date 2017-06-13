from tendrl.commons.flows import utils

def test_to_camel_case():
    snake_str = "test_camel_case"
    ret = utils.to_camel_case(snake_str)
    assert ret == "TestCamelCase"
