sample_definition = {
    'tendrl.gluster_integration': {
        'objects': {
            'Volume': {
                'flows': {
                    'StartVolume': {
                        'post_run': [
                            'tendrl.gluster_integration.objects.'
                            'volume.atoms.volume_started'
                        ],
                        'inputs': {
                            'mandatory': [
                                'Volume.volname'
                            ]
                        },
                        'run': 'tendrl.gluster_integration.objects.'
                        'Volume.flows.start_volume.StartVolume',
                        'description': 'Start Volume',
                        'pre_run': [
                            'tendrl.gluster_integration.objects'
                            '.volume.atoms.volume_exists'
                        ],
                        'enabled': True,
                        'atoms': [
                            'tendrl.gluster_integration.objects'
                            '.volume.atoms.start'
                        ],
                        'version': 1,
                        'type': 'Start',
                        'uuid': '1951e821-7aa9-4a91-8183-e73bc8275b6e'
                    },
                    'DeleteVolume': {
                        'post_run': [
                            'tendrl.gluster_integration.objects.volume'
                            '.atoms.volume_not_exists'
                        ],
                        'inputs': {
                            'mandatory': [
                                'Volume.volname',
                                'Volume.vol_id'
                            ]
                        },
                        'run': 'tendrl.gluster_integration.objects.Volume'
                        '.flows.delete_volume.DeleteVolume',
                        'description': 'Delete Volume',
                        'pre_run': [
                            'tendrl.gluster_integration.objects'
                            '.volume.atoms.volume_exists'
                        ],
                        'enabled': True,
                        'atoms': [
                            'tendrl.gluster_integration.objects'
                            '.volume.atoms.delete'
                        ],
                        'version': 1,
                        'type': 'Delete',
                        'uuid': '1951e821-7aa9-4a91-8183-e73bc8275b9e'
                    },
                },
                'enabled': True,
                'attrs': {
                    'redundancy_count': {
                        'type': 'Integer',
                        'help': 'Redundancy count of volume'
                    },
                    'force': {
                        'type': 'Boolean',
                        'help': 'If force execute the action'
                    },
                    'bricks': {
                        'type': 'List',
                        'help': 'List of brick mnt_paths for volume'
                    },
                },
                'value': 'clusters/$Tendrl_context.cluster_id'
                '/Volumes/$Volume.vol_id/',
                'atoms': {
                    'start': {
                        'inputs': {
                            'mandatory': [
                                'Volume.volname'
                            ]
                        },
                        'run': 'tendrl.gluster_integration.objects'
                        '.volume.atoms.start.Start',
                        'uuid': '242f6190-9b37-11e6-950d-a24fc0d9651c',
                        'type': 'Start',
                        'enabled': True,
                        'name': 'start_volume'
                    },
                }
            }
        },
        'flows': {
            'CreateVolume': {
                'post_run': [
                    'tendrl.gluster_integration.objects.'
                    'volume.atoms.volume_exists'
                ],
                'inputs': {
                    'mandatory': [
                        'Volume.volname', 'Volume.bricks'
                    ],
                    'optional': [
                        'Volume.stripe_count',
                        'Volume.replica_count',
                        'Volume.arbiter_count',
                        'Volume.disperse_count',
                        'Volume.disperse_data_count',
                        'Volume.redundancy_count',
                        'Volume.transport',
                        'Volume.force'
                    ]
                },
                'run': 'tendrl.gluster_integration.'
                'flows.create_volume.CreateVolume',
                'description': 'Create Volume with bricks',
                'pre_run': [
                    'tendrl.gluster_integration.objects.'
                    'volume.atoms.volume_not_exists'
                ],
                'enabled': True,
                'atoms': [
                    'tendrl.gluster_integration.objects.volume.atoms.create'
                ],
                'version': 1,
                'type': 'Create',
                'uuid': '1951e821-7aa9-4a91-8183-e73bc8275b8e'
            }
        }
    }
}
