from tendrl.commons.flows import utils


class TestFlowUtils(object):
    def test_to_camel_case(self):
        ret_val = utils.to_camel_case("its_my_testing_string")
        assert ret_val == "ItsMyTestingString"
