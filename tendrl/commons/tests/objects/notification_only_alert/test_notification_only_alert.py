from tendrl.commons.objects.notification_only_alert \
    import NotificationOnlyAlert


def test_render():
    noa_obj = NotificationOnlyAlert()
    noa_obj.render()
