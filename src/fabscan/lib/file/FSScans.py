__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
import base64
import shutil
import logging
import glob
import json
from PIL import Image

from fabscan.lib.util.FSUtil import json2obj
from fabscan.FSConfig import ConfigInterface
from fabscan.lib.util.FSInject import inject
import threading

@inject(
    config=ConfigInterface
)
class FSScans():

    def __init__(self, config):
        self.config = config
        self._logger = logging.getLogger(__name__)

    def not_valid(self):
        json = dict()
        json['response'] = "Not Valid"
        return json


    def get_scan_files(self, scan_id):
        scan_dir = self.config.file.folders.scans + scan_id
        files = glob.glob(scan_dir + '/scan_*.[p][l][y]')
        return files


    def get_list_of_scans(self, host):
        basedir = self.config.file.folders.scans

        subdirectories = sorted(os.listdir(str(basedir)), reverse=True)
        response = dict()
        response['scans'] = []

        for dir in subdirectories:
            if dir != "debug" and dir != 'calibration':
                if any(File.endswith(".ply") for File in os.listdir(basedir + dir)):
                    scan = dict()
                    scan['id'] = str(dir)
                    if os.path.os.path.exists(basedir + dir + "/scan_" + dir + "_both.ply"):
                        scan['pointcloud'] = str("http://" + host + "/scans/" + dir + "/scan_" + dir + "_both.ply")
                    else:
                        scan['pointcloud'] = str("http://" + host + "/scans/" + dir + "/scan_" + dir + "_0.ply")

                    scan['thumbnail'] = str("http://" + host + "/scans/" + dir + "/thumbnail_" + dir + ".png")
                    response['scans'].append(scan)

        return response


    def get_scan_by_id(self, host, id):
        basedir = self.config.file.folders.scans

        scan = dict()
        scan['id'] = id

        raw_scan_list = []
        mesh_list = []

        for file in os.listdir(basedir + "/" + id):
            prefix = file.split("_")[0]
            if 'scan' in prefix:
                raw_scan = dict()
                raw_scan['name'] = file
                raw_scan['url'] = str("http://" + host + "/api/v1/scans/" + id + "/downloads/" + file)
                raw_scan_list.append(raw_scan)

            elif 'mesh' in prefix:
                mesh = dict()
                mesh['name'] = file
                mesh['url'] = str("http://" + host + "/api/v1/scans/" + id + "/downloads/" + file)
                mesh_list.append(mesh)

        scan['raw_scans'] = raw_scan_list
        scan['meshes'] = mesh_list

        thumbnail_file = str("http://" + host + "/scans/" + id + "/thumbnail_" + id + ".png")
        if os.path.exists(basedir + id + "/thumbnail_" + id + ".png"):
            scan['thumbnail'] = thumbnail_file

        settings_file = str("http://" + host + "/scans/" + id + "/" + id + ".fab")
        if os.path.exists(basedir + id + "/" + id + ".fab"):
            scan['settings'] = settings_file

        return scan

    def delete_async(self, path):
        threading.Thread(target=lambda: shutil.rmtree(path, ignore_errors=True)).start()

    def delete_file(self, scan_id, file_name):
        file = self.config.file.folders.scans + scan_id + "/" + file_name
        #self.delete_async(file)
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
        dir_name = self.config.file.folders.scans + id
        self.delete_async(dir_name)
        #shutil.rmtree(dir_name, ignore_errors=True)
        response = dict()
        response['scan_id'] = id
        response['response'] = "SCAN_DELETED"

        return response


    def create_preview_image(self, base_64_image, scan_id):

        dir_name = self.config.file.folders.scans

        png = base64.decodebytes(base_64_image[22:])
        image_file = open(dir_name + scan_id + "/" + scan_id + ".png", "wb")
        image_file.write(png)

        preview_image = dir_name + scan_id + "/" + scan_id + ".png"
        thumbnail_image = dir_name + scan_id + "/thumbnail_" + scan_id + ".png"

        image_file.close()
        image_file = Image.open(preview_image)
        image_file.thumbnail((160, 120), Image.ANTIALIAS)
        image_file.save(thumbnail_image)

        response = dict()
        response['preview_image'] = preview_image
        response['thumbnail_image'] = thumbnail_image
        response['response'] = "PREVIEW_IMAGE_SAVED"

        return response

