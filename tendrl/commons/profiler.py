import sys

def start():
  import atexit
  import GreenletProfiler
  
  GreenletProfiler.set_clock_type('cpu')
  GreenletProfiler.start()
  sys.stdout.write("Started Tendrl profiling...")

  @atexit.register
  def finish():
    GreenletProfiler.stop()
    sys.stdout.write("Stopped Tendrl profiling...")
    stats = GreenletProfiler.get_func_stats()

    for stat_type in ['pstat', 'callgrind', 'ystat']:
        _stat_path = "/var/lib/tendrl/profiling/{0}/last_run_func_stat.{1}".format(NS.publisher_id,
                                                                                    stat_type)
        stats.save(_stat_path, type=stat_type)
        
    sys.stdout.write("Saved Tendrl profiling stats at ('/var/lib/tendrl/profiling/{0}/'.format(NS.publisher_id))")
