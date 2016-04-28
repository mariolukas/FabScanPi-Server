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
import logging


class FSRest():
    def __init__(self):
        self._logger =  logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.config = Config.instance()

    def call(self, path, data):

        path_elements = path.split("/")
        path_length = len(path_elements)

        action = data.get('Access-Control-Request-Method')
        action = "GET" if not action else action


        if path_length == 4:
            root_property = path_elements[-1]

            # /api/<version>/scans
            if "scans" == root_property:
                output = self.get_list_of_scans(data)

            # /api/<version>/filters
            elif "filters" == root_property:
                output = self.get_list_of_meshlab_filters()

        elif path_length == 5:
            root_property = path_elements[-2]
            root_id = path_elements[-1]

            # /api/<version>/scans/<scan_id>
            if "scans" == root_property:
                if "GET" == action:
                    output = self.get_scan_by_id(data, root_id)
                elif "DELETE" == action:
                    output = self.delete_scan(data, root_id)

            # /api/<version>/filer/<name>
            if "filter" == root_property:
                if "GET" == action:
                    pass
                elif "DELETE" == action:
                    pass

        elif path_elements == 6:
            root_property = path_elements[-4]
            root_id = path_elements[-3]
            node_property = [-2]

            #/api/<version>/scans/<scan_id>/files
            if "files" == node_property:
                pass

        elif path_elements == 7:
            root_property = path_elements[-4]
            root_id = path_elements[-3]
            node_property = [-2]
            node_id = path_elements[-1]

            # /api/<version>/scans/<scan_id>/files/<file_id>
            if "scans" == root_property:
                if "files" == node_property:
                    if "GET" == action:
                        pass
                    elif "DELETE" == action:
                        output = self.delete_file(root_id, node_id)


        else:
            output = self.not_valid()

        return json.dumps(output)


    def not_valid(self):
        json = dict()
        json['response'] = "Not Valid"
        return json


    def get_list_of_meshlab_filters(self):
        basedir = os.path.dirname(os.path.dirname(__file__))

        filters = dict()
        filters['filters'] = []
        for file in os.listdir(basedir+"/mlx"):
            if file.endswith(".mlx"):
                if os.path.os.path.exists(basedir+"/mlx/"+file):
                    filter = dict()
                    name, extension = os.path.splitext(file)

                    filter['name'] = name
                    filter['file_name'] = file

                    filters['filters'].append(filter)

        #encoded_json = json.dumps(filters)
        return filters

    def get_list_of_scans(self, headers):
        basedir = self.config.folders.scans

        subdirectories = os.listdir(str(basedir))
        scans = dict()
        scans['scans'] = []

        for dir in subdirectories:
            if dir != "debug":
                if os.path.os.path.exists(basedir+dir+"/scan_"+dir+".ply"):
                    scan = dict()
                    scan['id'] = str(dir)
                    scan['pointcloud'] =  str("http://"+headers['host']+"/scans/"+dir+"/scan_"+dir+".ply")
                    scan['thumbnail'] = str("http://"+headers['host']+"/scans/"+dir+"/thumbnail_"+dir+".png")
                    scans['scans'].append(scan)

        #encoded_json = json.dumps(scans)
        return scans

    def get_scan_by_id(self, headers, id):

        basedir = self.config.folders.scans

        scan = dict()
        scan['id'] = id

        raw_scan_list = []
        mesh_list = []

        for file in os.listdir(basedir+"/"+id):
            prefix = file.split("_")[0]
            if 'scan' in prefix:
                raw_scan = dict()
                raw_scan['name'] = file
                raw_scan['url'] = str("http://"+headers['host']+"/scans/"+id+"/"+file)
                raw_scan_list.append(raw_scan)

            elif 'mesh' in prefix:
                mesh = dict()
                mesh['name'] = file
                mesh['url'] = str("http://"+headers['host']+"/scans/"+id+"/"+file)
                mesh_list.append(mesh)

        scan['raw_scans'] = raw_scan_list
        scan['meshes'] = mesh_list

        thumbnail_file = str("http://"+headers['host']+"/scans/"+id+"/thumbnail_"+id+".png")
        if os.path.exists(basedir+id+"/thumbnail_"+id+".png"):
            scan['thumbnail'] = thumbnail_file

        settings_file = str("http://"+headers['host']+"/scans/"+id+"/"+id+".fab")
        if os.path.exists(basedir+id+"/"+id+".fab"):
            scan['settings'] = settings_file

        #encoded_json = json.dumps(scan)
        return scan

    def delete_scan(self, headers, id):

        dir_name = self.config.folders.scans+id
        print dir_name
        shutil.rmtree(dir_name, ignore_errors=True)
        response = dict()
        response['scan_id'] = id
        response['response'] = "SCAN DELETED"
        #encoded_json = json.dumps(response)

        return response

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