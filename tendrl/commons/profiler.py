import os
import sys


def start():
    # enable profling by adding to local conf.yaml "with_internal_profiling:
    #  True"
    # required: "pip install GreenletProfiler"
    # Provides function stats in formats 'pstat', 'callgrind', 'ystat'
    # stats are saved at "/var/lib/tendrl/profiling/$NS.publisher_id
    # /last_run_func_stat.$stat_type"
    # eg: tendrl-node-agent :
    # /var/lib/tendrl/profiling/node_agent/last_run_func_stat.pstat

    import atexit
    import GreenletProfiler

    GreenletProfiler.set_clock_type('cpu')
    GreenletProfiler.start()
    sys.stdout.write("\nStarted Tendrl profiling...")

    @atexit.register
    def finish():
        GreenletProfiler.stop()
        sys.stdout.write("\nStopped Tendrl profiling...")
        stats = GreenletProfiler.get_func_stats()
        _base_path = "/var/lib/tendrl/profiling/{0}/".format(NS.publisher_id)
        if not os.path.exists(_base_path):
            os.makedirs(_base_path)

        for stat_type in ['pstat', 'callgrind', 'ystat']:
            _stat_file = "last_run_func_stat.{0}".format(stat_type)
            _stat_path = os.path.join(_base_path, _stat_file)
            stats.save(_stat_path, type=stat_type)

        sys.stdout.write("\nSaved Tendrl profiling stats at %s" % _base_path)
