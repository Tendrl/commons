from mock import MagicMock

from tendrl.commons.flows import base_flow


class MyFlow(base_flow.BaseFlow):
    def __init__(
            self,
            name,
            atoms,
            help,
            enabled,
            inputs,
            pre_run,
            post_run,
            type,
            uuid,
            parameters,
            job,
            definitions
    ):
        super(MyFlow, self).__init__(
            name,
            atoms,
            help,
            enabled,
            inputs,
            pre_run,
            post_run,
            type,
            uuid,
            parameters,
            job,
            definitions
        )

    def run(self):
        super(MyFlow, self).run()


class TestBaseFlow(object):
    def setup_method(self):
        self.atoms = {
            'atom1': {
                'name': 'atom1',
                'enabled': True,
                'run': 'tendrl.dummymodule.objects.myobject.atom1.Atom1',
                'help': 'atom1',
                'uuid': '61959242-628f-4847-a5e2-2c8d8daac0cd',
                'inputs': {
                    'mandatory': ['myobject.field1', 'myobject.field2']
                }
            }
        }

        self.flow_inputs = {
            'mandatory': ['myobject.field1', 'myobject.field2']
        }

        self.flow_pre_run = \
            ['tendrl.dummymodule.objects.myobject.atoms.pre_run1']
        self.flow_post_run = \
            ['tendrl.dummymodule.objects.myobject.atoms.post_run1']
        self.flow_parameters = {
            'Tendrl_context.cluster_id':
                "61959242-628f-4847-a5e2-2c8d8daac0ab",
            'etcd_orm': MagicMock(),
            'config': MagicMock(),
            'manager': MagicMock()
        }
        self.job = {
            'cluster_id': "61959242-628f-4847-a5e2-2c8d8daac0ab",
            'type': 'sds',
            'run': 'tendrl.dummymodule.flows.dummy_flow.DummyFlow',
            'status': 'new',
            'parameters': {
                'Tendrl_context.clusrer_id':
                    "61959242-628f-4847-a5e2-2c8d8daac0ab",
                'myobject.field1': 'val1',
                'myobject.field2': 'val2'
            },
            "request_id": "/clusters/61959242-628f-4847-a5e2-2c8d8daac0ab"
                          "/_jobs/tendrl.dummymodule.flows.dummy_flow"
                          ".DummyFlow_1"
        }
        self.definitions = {
            'tendrl.dummymodule': {
                'objects': {
                    'myobject': {
                        'enabled': True,
                        'value': '',
                        'attrs': {
                            'field1': {
                                'help': 'field1',
                                'type': 'String'
                            },
                            'field2': {
                                'help': 'field2',
                                'type': 'String'
                            }
                        },
                        'atoms': {
                            'atom1': {
                                'name': 'atom1',
                                'enabled': True,
                                'run':
                                'tendrl.dummymodule.objects.myobject.atoms.'
                                    'atom1.Atom1',
                                'help': 'atom1',
                                'uuid':
                                    '61959242-628f-4847-a5e2-2c8d8daac0cd',
                                'inputs': {
                                    'mandatory':
                                        ['myobject.field1', 'myobject.field2']
                                }
                            },
                            'pre_run1': {
                                'name': 'pre_run1',
                                'enabled': True,
                                'run':
                                'tendrl.dummymodule.objects.myobject.atoms.'
                                    'pre_run1.PreRun1',
                                'help': 'atom1',
                                'uuid':
                                    '61959242-628f-4847-a5e2-2c8d8daac0c3',
                                'inputs': {
                                    'mandatory':
                                        ['myobject.field1', 'myobject.field2']
                                }
                            },
                            'post_run1': {
                                'name': 'post_run1',
                                'enabled': True,
                                'run':
                                'tendrl.dummymodule.objects.myobject.atoms.'
                                    'post_run1.PostRun1',
                                'help': 'atom1',
                                'uuid':
                                    '61959242-628f-4847-a5e2-2c8d8daac0c4',
                                'inputs': {
                                    'mandatory':
                                        ['myobject.field1', 'myobject.field2']
                                }
                            }
                        }
                    }
                },
                'flows': {
                    'dummy_flow': {
                        'atoms': [
                            'tendrl.dummymodule.objects.myobject.atoms.atom1'
                        ],
                        'help': 'dummy_flow',
                        'enabled': True,
                        'inputs': {
                            'mandatory': [
                                'Tendrl_context.cluster_id',
                                'myobject.field1',
                                'myobject.field2'
                            ]
                        },
                        'pre_run': [
                            'tendrl.dummymodule.objects.myobject.atoms.'
                            'pre_run1'
                        ],
                        'post_run': [
                            'tendrl.dummymodule.objects.myobject.atoms.'
                            'post_run1'
                        ],
                        'run': 'tendrl.dummymodule.flows.dummy_flow.DummyFlow',
                        'type': 'Create',
                        'uuid': '61959242-628f-4847-a5e2-2c8d8daac1cd',
                        'version': 1
                    }
                }
            }
        }
        base_flow.etcd_orm = MagicMock()
        base_flow.LOG = MagicMock()

        self.flow_obj = MyFlow(
            "DummyFlow",
            self.atoms,
            "Dummyflow",
            True,
            self.flow_inputs,
            self.flow_pre_run,
            self.flow_post_run,
            "Create",
            "61959242-628f-4847-a5e2-2c8d8daac0ca",
            self.flow_parameters,
            self.job,
            self.definitions
        )

    def test_run(self):
        self.flow_obj.execute_atom = MagicMock(
            return_value=True
        )
        self.flow_obj.run()
        self.flow_obj.execute_atom.assert_called()
        assert self.flow_obj.execute_atom.return_value is True

    def test_extract_atom_details(self):
        name, enabled, help, inputs, outputs, uuid = \
            self.flow_obj.extract_atom_details(
                "tendrl.dummymodule.objects.myobject.atoms.pre_run1",
            )
        assert name == "pre_run1"
        assert enabled is True
        assert help == "atom1"
        assert len(inputs['mandatory']) == 2
