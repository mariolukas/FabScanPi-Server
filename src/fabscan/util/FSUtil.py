__author__ = 'mariolukas'
import os
import json
import shutil
import subprocess
import shlex
import logging

from collections import namedtuple
from fabscan.FSConfig import Config

class FSSystem(object):
    def __init__(self):
        self._logger =  logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

    @staticmethod
    def run_command(command):
            process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    logging.getLogger(__name__).setLevel(logging.DEBUG)
                    logging.getLogger(__name__).debug(output.strip())
            rc = process.poll()
            return rc

    @staticmethod
    def isRaspberryPi(self):
        if os.uname()[4].startswith("arm"):
            return True
        else:
            return False

def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())

def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)

def new_message():
        message = dict()
        message['type'] = ""
        message['data'] = dict()

        return message

def delete_folder(folder):
    if os.path.isdir(folder):
        shutil.rmtree(folder, ignore_errors=True)


def delete_image_folders(scan_id):
    folder =  Config.instance().folders.scans+scan_id+"/color_raw/"
    delete_folder(folder)

    folder =  Config.instance().folders.scans+scan_id+"/laser_raw/"
    delete_folder(folder)


def delete_scan(scan_id,ignore_errors=True):

    #basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    folder =  Config.instance().folders.scans+scan_id+"/"

    if os.path.isdir(folder):
        shutil.rmtree(folder, ignore_errors=True)
    else:
         print "Nothing to delete..."

