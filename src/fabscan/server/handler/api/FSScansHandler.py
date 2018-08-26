import os
import json
import tornado.web

class FSScansHandler(tornado.web.RequestHandler):

    def initialize(self, config):
        self.config = config

    def get(self):
        scans = self.get_list_of_scans()
        self.write(json.dumps(scans))

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