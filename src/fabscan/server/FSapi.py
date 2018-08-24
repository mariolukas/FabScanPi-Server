__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
import json
import base64
import shutil
import logging
import glob
from PIL import Image

from fabscan.util.FSUtil import json2obj
from fabscan.FSConfig import ConfigInterface
from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.util.FSInject import inject

@inject(
    config=ConfigInterface,
    hardwarecontroller=FSHardwareControllerInterface
)
class FSRest():
    def __init__(self, config, hardwarecontroller):

        self.config = config
        self.hardwarecontroller = hardwarecontroller
        self._logger = logging.getLogger(__name__)

    def call(self,action, path, headers, data=None):

        output = dict()

        path_elements = path.split("/")
        path_length = len(path_elements)

        if path_length == 4:
            root_property = path_elements[-1]

            # /api/<version>/scans
            if "scans" == root_property:
                output = self.get_list_of_scans(headers)

            # /api/<version>/filters
            elif "filters" == root_property:
                output = self.get_list_of_meshlab_filters()

            elif "devices" == root_property:
                output = self.hardwarecontroller.get_devices_as_json()

        elif path_length == 5:
            root_property = path_elements[-2]
            root_id = path_elements[-1]

            # /api/<version>/scans/<scan_id>
            if "scans" == root_property:
                if "GET" == action:
                    output = self.get_scan_by_id(headers, root_id)
                elif "DELETE" == action:
                    output = self.delete_scan(root_id)

            # /api/<version>/filter/<name>
            #if "filter" == root_property:
            #    if "GET" == action:
            #        pass
            #    elif "DELETE" == action:
            #        pass

        elif path_length == 6:
            root_property = path_elements[-3]
            root_id = path_elements[-2]
            node_property = path_elements[-1]


            #/api/<version>/scans/<scan_id>/files
            if "files" == node_property:
                pass
            #/api/<version>/scans/<scan_id>/previews
            if "previews" == node_property:
                if "POST" == action:
                    output = self.create_preview_image(data, root_id)

        elif path_length == 7:
            root_property = path_elements[-4]
            root_id = path_elements[-3]
            node_property = path_elements[-2]
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

    def get_scan_files(self, scan_id):
        scan_dir = self.config.folders.scans+scan_id
        files = glob.glob(scan_dir+'/scan_*.[p][l][y]')
        return files


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

        return filters

    def get_list_of_scans(self, headers):
        basedir = self.config.folders.scans

        subdirectories = sorted(os.listdir(str(basedir)),reverse=True)
        response = dict()
        response['scans'] = []

        for dir in subdirectories:
            if dir != "debug":
                if os.path.os.path.exists(basedir+dir+"/scan_"+dir+".ply"):
                    scan = dict()
                    scan['id'] = str(dir)
                    scan['pointcloud'] =  str("http://"+headers['host']+"/scans/"+dir+"/scan_"+dir+".ply")
                    scan['thumbnail'] = str("http://"+headers['host']+"/scans/"+dir+"/thumbnail_"+dir+".png")
                    response['scans'].append(scan)

        return response

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

        return scan

    def delete_file(self, scan_id, file_name):
        file = self.config.folders.scans+scan_id+"/"+file_name

        os.unlink(file)

        if len(self.get_scan_files(scan_id)) == 0:
            response = self.delete_scan(scan_id)
        else:
            response = dict()
            response['file_name'] = file_name
            response['scan_id'] = scan_id
            response['response'] = "FILE_DELETED"

        return response

    def delete_scan(self, id):

        dir_name = self.config.folders.scans+id
        shutil.rmtree(dir_name, ignore_errors=True)

        response = dict()
        response['scan_id'] = id
        response['response'] = "SCAN_DELETED"

        return response

    def create_preview_image(self, data, scan_id):

        object = json2obj(str(data))

        dir_name =  self.config.folders.scans
        png = base64.decodestring(object.image[22:])
        image_file = open(dir_name+scan_id+"/"+scan_id+".png", "w")
        image_file.write(png)

        preview_image = dir_name+scan_id+"/"+scan_id+".png"
        thumbnail_image = dir_name+scan_id+"/thumbnail_"+scan_id+".png"

        image_file.close()
        image_file = Image.open(preview_image)
        image_file.thumbnail((160,120),Image.ANTIALIAS)
        image_file.save(thumbnail_image)

        response = dict()
        response['preview_image'] = preview_image
        response['thumbnail_image'] = thumbnail_image
        response['response'] = "PREVIEW_IMAGE_SAVED"

        return response