__author__ = 'mariolukas'
import os
import json
import shutil
import subprocess
import shlex
import logging
import glob
import signal
import zipfile

from collections import namedtuple
from fabscan.FSConfig import ConfigInterface
from fabscan.lib.util.FSInject import inject


class FSSystemExit(object):

    def __init__(self):
        self.kill = False
        self._logger = logging.getLogger(__name__)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self._logger.debug("System Exit initiated...")
        self.kill = True

class FSSystemInterface(object):
    def __init__(self, config):
        pass

@inject(
    config=ConfigInterface
)
class FSSystem(object):
    def __init__(self, config):
        self._logger = logging.getLogger(__name__)
        self.config = config

    @staticmethod
    def run_command(command, blocking=False):

            if blocking:
                process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                output, _ = process.communicate()
                if output:
                   logging.getLogger(__name__).debug(output.rstrip("\n"))
                rc = process.returncode
            else:
                process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        logging.getLogger(__name__).debug(output.rstrip("\n"))
                process.poll()

                rc = process.returncode

            return rc

    @staticmethod
    def isRaspberryPi(self):
        if os.uname()[4].startswith("arm"):
            return True
        else:
            return False


    def delete_folder(self, folder):
        if os.path.isdir(folder):
            shutil.rmtree(folder, ignore_errors=True)


    def delete_image_folders(self,scan_id):
        folder = self.config.folders.scans+scan_id+"/color_raw/"
        self.delete_folder(folder)

        folder = self.config.folders.scans+scan_id+"/laser_raw/"
        self.delete_folder(folder)


    def delete_scan(self, scan_id, ignore_errors=True):

        #basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        folder = self.config.folders.scans+scan_id+"/"

        mask = self.config.folders.scans+scan_id+"/"'*.[pso][ltb][lyj]'
        number_of_files = len(glob.glob(mask))

    def zipdir(self, scan_id):
        # ziph is zipfile handle
        zipf = zipfile.ZipFile(self.config.folders.scans+scan_id+'/'+str(scan_id)+'.zip', 'w', zipfile.ZIP_DEFLATED)

        for root, dirs, files in os.walk(self.config.folders.scans+scan_id+"/color_raw/"):
            for file in files:
                zipf.write(os.path.join(root, file))

        zipf.close()

def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())

def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)

def new_message():
        message = dict()
        message['type'] = ""
        message['data'] = dict()

        return message



    #if os.path.isdir(folder):
    #    shutil.rmtree(folder, ignore_errors=True)
    #else:
    #     print "Nothing to delete..."

