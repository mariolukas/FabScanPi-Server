__author__ = 'mariolukas'
import os
import json
import shutil
from collections import namedtuple
from fabscan.FSConfig import Config

def isRaspberryPi():
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

