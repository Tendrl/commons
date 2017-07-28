import maps


class Plugin(object):
    def __init__(self, *args, **kwargs):
        self.monitor_secret = "Test_monitor"

    def get_plugin(self, *args, **kwargs):
        return self

    def install_mon(self, *args, **kwargs):
        return "test_task_id"

    def task_status(self, *args, **kwargs):
        if args[0] == "task_id_test":
            return maps.NamedDict(ended=True, succeeded=False)
        if args[0] == "task_test_id":
            return maps.NamedDict(ended=False, succeeded=False)
        if args[0] == "ret_none":
            return {}
        return maps.NamedDict(ended=True, succeeded=True)

    def install_osd(self, *args, **kwargs):
        return "test_task_id"

    def configure_mon(self, *args, **kwargs):
        return "test_task_id"

    def configure_osd(self, *args, **kwargs):
        return "test_task_id"

    def Journal(self, *args, **kwargs):
        return self

    def save(self, *args, **kwargs):
        return None

    def setup_gluster_node(self, *args, **kwargs):
        if kwargs["repo"] == "test_gluster":
            return False
        return True

    def create_gluster_cluster(self, *args, **kwargs):
        if args[0][0] == "test":
            return False
        return True

    def expand_gluster_cluster(self, *args, **kwargs):
        if args[0][0] == "test":
            return False
        return True

    def setup(self):
        return "ssh_key", "No error"
