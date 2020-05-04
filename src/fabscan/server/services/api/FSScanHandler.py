import os
import json
import glob
import shutil
import logging
import tornado.web
from fabscan.lib.file.FSScans import FSScans
from fabscan.server.services.api.FSBaseHandler import BaseHandler

class FSScanHandler(BaseHandler):

    def initialize(self, *args, **kwargs):
        self._logger = logging.getLogger(__name__)
        self.config = kwargs.get('config')
        self.scanlib = FSScans()
        #self._logger.debug(kwargs)

    def delete(self, *args, **kwargs):
        scan_id = kwargs.get('scan_id')
        filename = self.get_argument('filename', True)
        response = self.scanlib.delete_file(scan_id, filename)
        self.write(json.dumps(response))

    def get(self, scan_id=None):
        if scan_id is None:
             scans = self.scanlib.get_list_of_scans(self.request.host)
             self.write(json.dumps(scans))
        else:
             self._logger.debug(scan_id)
             files = self.scanlib.get_scan_by_id(self.request.host, scan_id)
             self.write(json.dumps(files))

    def post(self, *args, **kwargs):
        scan_id = kwargs.get('scan_id')
        data = tornado.escape.json_decode(self.request.body)
        response = self.scanlib.create_preview_image(data['image'].encode(), scan_id)
        self.write(json.dumps(response))