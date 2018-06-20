from tendrl.commons.objects.definition import Definition

def test_get_parsed_defs():
	definition_obj = Definition()
	definition_obj._parsed_defs = None
	definition_obj.get_parsed_defs()