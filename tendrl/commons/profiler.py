import os
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
    _base_path = "/var/lib/tendrl/profiling/{0}/".format(NS.publisher_id)
    if not os.path.exists(_base_path):
        os.makedirs(_base_path)
            
    for stat_type in ['pstat', 'callgrind', 'ystat']:
        _stat_file = "last_run_func_stat.{0}".format(stat_type)
        _stat_path = os.path.join(_base_path, _stat_file)
        stats.save(_stat_path, type=stat_type)
        
    sys.stdout.write("Saved Tendrl profiling stats at %s" % _base_path)
