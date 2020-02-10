import threading
import logging
import os

from fabscan.lib.util.FSUtil import FSSystem
from fabscan.FSEvents import FSEventManagerInterface, FSEvents
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.lib.util.FSInject import inject
from xml.dom import minidom
import xml

@inject(
    config=ConfigInterface,
    settings=SettingsInterface,
    eventmanager=FSEventManagerInterface
)
class FSMeshlabTask(threading.Thread):
        def __init__(self, id, filter, format, file, eventmanager, config, settings):
            threading.Thread.__init__(self)
            self.eventManager = eventmanager.instance
            self.settings = settings
            self.config = config
            self._logger = logging.getLogger(__name__)

            self.file = file
            self.scan_id = id
            self.filter = filter
            self.format = format

        def get_poitcloud_value_by_line(self, pointcloud_file, lookup):
            with open(pointcloud_file) as myFile:
                for num, line in enumerate(myFile, 1):
                    if lookup in line:
                        number_of_pints = int(list(filter(str.isdigit, line)))
                        return number_of_pints

        def prepare_down_sampling(self, file, pointcloud_size):

            try:
                xmldoc = minidom.parse(file)
                #itemlist = xmldoc.getElementsByTagName('filter')
                params = xmldoc.getElementsByTagName('Param')
                for param in params:
                    if param.attributes['name'].value == "SampleNum":
                        param.setAttribute('value', str(int(pointcloud_size/3)))

            except xml.parsers.expat.ExpatError as ex:
                print(ex)

            with open(file, "wb") as fh:
                xmldoc.writexml(fh)

        def run(self):
            self._logger.info("Process started...")

            data = {
                "message": "MESHING_STARTED",
                "level": "info"
            }
            self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, data)

            basedir = os.path.dirname(os.path.dirname(__file__))
            mlx_script_path = basedir+"/mlx/"+self.filter

            input = self.config.file.folders.scans+str(self.scan_id)+"/"+str(self.file)
            output = self.config.file.folders.scans+str(self.scan_id)+"/mesh_"+str(self.file[:-3])+"_"+str(self.filter).split(".")[0]+"."+self.format
            self._logger.info(output)

            pointcloud_size = self.get_poitcloud_value_by_line(pointcloud_file=input, lookup="element vertex")
            self.prepare_down_sampling(str(mlx_script_path), pointcloud_size)

            return_code = FSSystem.run_command("xvfb-run meshlabserver -i "+input+" -o "+output+" -s "+str(mlx_script_path)+" -om vc vn")
            self._logger.debug("Process return code: " + str(return_code))

            if return_code is 0:

                message = {
                    "message": "MESHING_DONE",
                    "scan_id": self.scan_id,
                    "level": "success"
                }

            else:
                message = {
                    "message": "MESHING_FAILED",
                    "scan_id": self.scan_id,
                    "level": "error"
                }

            self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
            self._logger.info("Process finished.")
