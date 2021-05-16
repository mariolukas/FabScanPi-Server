import tracemalloc
import logging

class FSMemoryProfiler:
    def __init__(self):
         self._logger = logging.getLogger(__name__)
         tracemalloc.start(25)
         self.start_snap = tracemalloc.take_snapshot()
         self.prev_stats = None
         self.curr_snap = self.start_snap
         self.prev_snap = self.start_snap

    def debug_memory(self, top=20, trace=1):
        try:
            self.curr_snap = tracemalloc.take_snapshot()
            stats = self.curr_snap.compare_to(self.start_snap, 'filename')
            self.prev_stats = self.curr_snap.compare_to(self.prev_snap, 'lineno')

            self._logger.debug("Top Diffs since start")
            for i, stat in enumerate(stats[:top], 1):
                self._logger.debug("top_diffs %i %s", i, str(stat))

            self._logger.debug("Top Incemental")
            for i, stat in enumerate(self.prev_stats[:top], 1):
                self._logger.debug("top_diffs %i %s", i, str(stat))

            self._logger.debug("Tracebaks")
            traces = self.curr_snap.statistics("traceback")
            for stat in traces[:trace]:
                self._logger.debug("traceback %i  %i", stat.count, stat.size/ 1024)
                for line in stat.traceback.format():
                    self._logger.debug(line)

            self.prev_snap = self.curr_snap
        except Exception as e:
            self._logger.error(e)






