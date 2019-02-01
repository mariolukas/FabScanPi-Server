import os
import json
import glob
import shutil
import logging
import tornado.web
from fabscan.lib.file.FSScans import FSScans
from fabscan.server.services.api.FSBaseHandler import BaseHandler

class FSDeviceHandler(BaseHandler):

    def initialize(self, *args, **kwargs):
        self._logger = logging.getLogger(__name__)
        self.config = kwargs.get('config')
        self.hardwarecontroller = kwargs.get('hardwarecontroller')

    def get(self):
        devices = self.hardwarecontroller.get_devices_as_json()
        self.write(json.dumps(devices))
