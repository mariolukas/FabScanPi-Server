import threading
import logging
import os
from fabscan.FSSettings import Settings
from fabscan.FSConfig import Config
from fabscan.util.FSUtil import FSSystem
from fabscan.FSEvents import FSEventManager, FSEvents
from fabscan.util import FSUtil


class FSMeshlabTask(threading.Thread):
        def __init__(self, prefix):
            threading.Thread.__init__(self)
            self.eventManager = FSEventManager.instance()
            self._logger =  logging.getLogger(__name__)
            self._logger.setLevel(logging.DEBUG)
            self.settings = Settings.instance()
            self.config = Config.instance()
            self.prefix = prefix

        def run(self):
            try:
                self._logger.info("Meshlab Process Started...")
                basedir = os.path.dirname(os.path.dirname(__file__))

                script_name = "simple_meshing.mlx"
                mlx = basedir+"/mlx/"+script_name

                input =  self.config.folders.scans+str(self.prefix)+"/scan_"+str(self.prefix)+".ply"
                output = self.config.folders.scans+str(self.prefix)+"/mesh_"+str(self.prefix)+"_"+script_name.split(".")[0]+".ply"

                FSSystem.run_command("xvfb-run meshlabserver -i "+input+" -o "+output+" -s "+str(mlx)+" -om vc vn")
                self.message_event()
                self._logger.info("Meshlab Process finished.")

            except:
                self._logger.error("Meshing Task crashed.")
                message = FSUtil.new_message()
                message['type'] = FSEvents.ON_INFO_MESSAGE
                message['data']['message'] = "MESHING_FAILED"
                message['data']['level'] = "error"
                self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)


        def message_event(self):
            message = FSUtil.new_message()
            message['type'] = FSEvents.ON_INFO_MESSAGE
            message['data']['message'] = "MESHING_DONE"
            message['data']['scan_id'] = self.prefix
            message['data']['level'] = "success"
            self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)