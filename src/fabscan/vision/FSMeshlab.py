import threading
import logging
import os
from fabscan.FSSettings import Settings
from fabscan.FSConfig import Config
from fabscan.util.FSUtil import FSSystem
from fabscan.FSEvents import FSEventManager, FSEvents
from fabscan.util import FSUtil


class FSMeshlabTask(threading.Thread):
        def __init__(self, id, filter, format):
            threading.Thread.__init__(self)
            self.eventManager = FSEventManager.instance()
            self._logger =  logging.getLogger(__name__)
            self._logger.setLevel(logging.DEBUG)
            self.settings = Settings.instance()
            self.config = Config.instance()
            self.scan_id = id
            self.filter = filter
            self.format = format

        def run(self):
            self._logger.info("Meshlab Process Started...")

            basedir = os.path.dirname(os.path.dirname(__file__))
            mlx_script_path = basedir+"/mlx/"+self.filter

            input =  self.config.folders.scans+str(self.scan_id)+"/scan_"+str(self.scan_id)+".ply"
            output = self.config.folders.scans+str(self.scan_id)+"/mesh_"+str(self.scan_id)+"_"+str(self.filter).split(".")[0]+"."+self.format
            self._logger.info(output)

            FSSystem.run_command("xvfb-run meshlabserver -i "+input+" -o "+output+" -s "+str(mlx_script_path)+" -om vc vn")

            message = {
                "message" : "MESHING_DONE",
                "scan_id" : self.scan_id,
                "level": "success"
            }
            self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE,message)
            self._logger.info("Meshlab Process finished.")
