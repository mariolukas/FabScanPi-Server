import json
import logging
from fabscan.server.services.api.FSBaseHandler import BaseHandler

class FSDeviceHandler(BaseHandler):

    def initialize(self, *args, **kwargs):
        self._logger = logging.getLogger(__name__)
        self.config = kwargs.get('config')
        self.hardwarecontroller = kwargs.get('hardwarecontroller')

    def get(self):
        devices = self.hardwarecontroller.get_devices_as_json()
        self.write(json.dumps(devices))
