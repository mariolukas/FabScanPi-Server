__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
import json
from PIL import Image
from fabscan.util.FSUtil import json2obj
from fabscan.FSConfig import Config
import base64
import shutil

class FSapi():
    def __init__(self):
        self.config = Config.instance()


    def get_list_of_scans(self, headers):
        basedir = self.config.folders.scans

        subdirectories = os.listdir(str(basedir))
        scans = dict()
        scans['scans'] = []

        for dir in subdirectories:
            if dir != "debug":
                pointcloud_file = str("http://"+headers['host']+"/scans/"+dir+"/"+dir+".ply")
                if os.path.os.path.exists(basedir+dir+"/"+dir+".ply"):
                    scan = dict()
                    scan['id'] = str(dir)
                    scan['pointcloud'] =  str("http://"+headers['host']+"/scans/"+dir+"/"+dir+".ply")
                    scan['thumbnail'] = str("http://"+headers['host']+"/scans/"+dir+"/thumbnail_"+dir+".png")
                    scans['scans'].append(scan)

        encoded_json = json.dumps(scans)
        return encoded_json

    def get_scan_by_id(self, headers, id):

        basedir = self.config.folders.scans

        scan = dict()
        scan['id'] = id

        pointcloud_file = str("http://"+headers['host']+"/scans/"+id+"/"+id+".ply")
        if os.path.exists(basedir+id+"/"+id+".ply"):
            scan['pointcloud'] = pointcloud_file

        thumbnail_file = str("http://"+headers['host']+"/scans/"+id+"/thumbnail_"+id+".png")
        if os.path.exists(basedir+id+"/thumbnail_"+id+".png"):
            scan['thumbnail'] = thumbnail_file

        mesh_file = str("http://"+headers['host']+"/scans/"+id+"/"+id+"_meshed.ply")
        if os.path.exists(basedir+id+"/"+id+"_meshed.ply"):
            scan['mesh'] = mesh_file

        settings_file = str("http://"+headers['host']+"/scans/"+id+"/"+id+".fab")
        if os.path.exists(basedir+id+"/"+id+".fab"):
            scan['settings'] = settings_file

        encoded_json = json.dumps(scan)
        return encoded_json

    def delete_scan(self, headers, id):

        dir_name = self.config.folders.scans+id
        print dir_name
        shutil.rmtree(dir_name, ignore_errors=True)
        response = dict()
        response['scan_id'] = id
        response['response'] = "SCAN DELETED"
        encoded_json = json.dumps(response)

        return encoded_json

    def save_preview_content(self, data, scan_id):
        print scan_id
        object = json2obj(str(data))

        dir_name =  self.config.folders.scans
        png = base64.decodestring(object.image[22:])
        image_file = open(dir_name+scan_id+"/"+scan_id+".png", "w")
        image_file.write(png)

        image_file.close()
        image_file = Image.open(dir_name+scan_id+"/"+scan_id+".png")
        image_file.thumbnail((160,120),Image.ANTIALIAS)
        image_file.save(dir_name+scan_id+"/thumbnail_"+scan_id+".png")