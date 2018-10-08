import maps


from tendrl.commons.objects.gluster_peer import GlusterPeer


def test_gluster_peer():
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = '77deef29-b8e5-4dc5-8247-21e2a'\
                                       '409a66a'
    obj = GlusterPeer(
        state="['Peer', 'Cluster', 'in']",
        connected="Connected",
        hostname="dhcp12-123.lab.abc.com",
        peer_uuid="53dfa0fa-edb2-4966-80b9-86ca981c7fcb"
    )
    out = [
        {'dir': False,
         'value': False,
         'name': 'deleted',
         'key': '/clusters/77deef29-b8e5-4dc5-8247-21e2a'
                '409a66a/nodes/1/Peers/53dfa0fa-edb2-4966-80b9-8'
                '6ca981c7fcb/deleted'
         },
        {'dir': False,
         'value': '',
         'name': 'deleted_at',
         'key': '/clusters/77deef29-b8e5-4dc5-8247-21e2a'
                '409a66a/nodes/1/Peers/53dfa0fa-edb2-4966-80b9-8'
                '6ca981c7fcb/deleted_at'
         },
        {'dir': False,
         'value': "['Peer', 'Cluster', 'in']",
         'name': 'state',
         'key': '/clusters/77deef29-b8e5-4dc5-8247-21e2a'
                '409a66a/nodes/1/Peers/53dfa0fa-edb2-4966-80b9-8'
                '6ca981c7fcb/state'
         },
        {'dir': False,
         'value': 'Connected',
         'name': 'connected',
         'key': '/clusters/77deef29-b8e5-4dc5-8247-21e2a'
         '409a66a/nodes/1/Peers/53dfa0fa-edb2-4966-80b9-86ca981c'
         '7fcb/connected'
         },
        {'dir': False,
         'value': '53dfa0fa-edb2-4966-80b9-86ca981c7fcb',
         'name': 'peer_uuid',
         'key': '/clusters/77deef29-b8e5-4dc5-8247-21e2a4'
                '09a66a/nodes/1/Peers/53dfa0fa-edb2-4966-80b9-86ca'
                '981c7fcb/peer_uuid'
         },
        {'dir': False,
         'value': 'dhcp12-123.lab.abc.com',
         'name': 'hostname',
         'key': '/clusters/77deef29-b8e5-4dc5-8247-21e2a40'
                '9a66a/nodes/1/Peers/53dfa0fa-edb2-4966-80b9-86ca9'
                '81c7fcb/hostname'
         },
        {'dir': False,
         'name': 'hash',
         'value': 'dfc2af50c23cdb7d3677782fd46041994d66538fecb82f51'
                  'eb155199b9e325a18c8cd6221bd2996ce3c973f42d81d988'
                  '812e366627cedd51cbda995912641605',
         'key': '/clusters/77deef29-b8e5-4dc5-8247-21e2a409a66a'
                '/nodes/1/Peers/53dfa0fa-edb2-4966-80b9-86ca'
                '981c7fcb/hash'
         }
    ]
    for result in obj.render():
        if result not in out:
            raise AssertionError
