import os
import json
import glob
import shutil
from fabscan.server.services.api.FSBaseHandler import FSBaseHandler

class FSScanHandler(FSBaseHandler):

    def initialize(self, config):
        self.config = config

    def get(self):
        scans = self.get_list_of_scans()
        self.write(json.dumps(scans))

    def get_scan_files(self, scan_id):
        scan_dir = self.config.folders.scans+scan_id
        files = glob.glob(scan_dir+'/scan_*.[p][l][y]')
        return files

    def get_list_of_scans(self):
        basedir = self.config.folders.scans

        subdirectories = sorted(os.listdir(str(basedir)),reverse=True)
        response = dict()
        response['scans'] = []

        for dir in subdirectories:
            if dir != "debug":
                if os.path.os.path.exists(basedir+dir+"/scan_"+dir+".ply"):
                    scan = dict()
                    scan['id'] = str(dir)
                    scan['pointcloud'] = str("http://"+self.request.host+"/scans/"+dir+"/scan_"+dir+".ply")
                    scan['thumbnail'] = str("http://"+self.request.host+"/scans/"+dir+"/thumbnail_"+dir+".png")
                    response['scans'].append(scan)

        return response

    def get_scan_by_id(self, id):

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
                raw_scan['url'] = str("http://"+self.request.host+"/scans/"+id+"/"+file)
                raw_scan_list.append(raw_scan)

            elif 'mesh' in prefix:
                mesh = dict()
                mesh['name'] = file
                mesh['url'] = str("http://"+self.request.host+"/scans/"+id+"/"+file)
                mesh_list.append(mesh)

        scan['raw_scans'] = raw_scan_list
        scan['meshes'] = mesh_list

        thumbnail_file = str("http://"+self.request.host+"/scans/"+id+"/thumbnail_"+id+".png")
        if os.path.exists(basedir+id+"/thumbnail_"+id+".png"):
            scan['thumbnail'] = thumbnail_file

        settings_file = str("http://"+self.request.host+"/scans/"+id+"/"+id+".fab")
        if os.path.exists(basedir+id+"/"+id+".fab"):
            scan['settings'] = settings_file

        return scan

    def delete_file_of_scan(self, scan_id, file_name):
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
