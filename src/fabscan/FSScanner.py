__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time
import threading
import logging
import json
import multiprocessing

from fabscan.FSVersion import __version__
from fabscan.FSEvents import FSEventManager, FSEvents
from fabscan.controller import HardwareController
from fabscan.util import FSUtil
from fabscan.util import FSUpdate
from fabscan.FSScanProcessor import FSScanProcessor
from fabscan.vision.FSMeshlab import FSMeshlabTask
from fabscan.FSSettings import Settings
from fabscan.FSScanProcessor import FSScanProcessorCommand


class FSState(object):
    IDLE = "IDLE"
    SCANNING = "SCANNING"
    SETTINGS = "SETTINGS"

class FSCommand(object):
    SCAN = "SCAN"
    START = "START"
    STOP = "STOP"
    UPDATE_SETTINGS = "UPDATE_SETTINGS"
    MESHING = "MESHING"
    _COMPLETE = "_COMPLETE"
    SCANNER_ERROR = "SCANNER_ERROR"


class FSScanner(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self._state = FSState.IDLE
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.settings = Settings.instance()
        self.daemon = True
        self.hardwareController = HardwareController.instance()
        self._exit_requested = False
        self.meshingTaskRunning = False

        self.scanProcessor = FSScanProcessor.start()
        self._logger.debug("Number of cpu cores: "+str( multiprocessing.cpu_count()))

        self.eventManager = FSEventManager.instance()
        self.eventManager.subscribe(FSEvents.ON_CLIENT_CONNECTED, self.on_client_connected)
        self.eventManager.subscribe(FSEvents.COMMAND, self.on_command)

    def run(self):

        while not self._exit_requested:
            self.eventManager.handle_event_q()
            time.sleep(0.05)

    def request_exit(self):
            self._exit_requested = True

    def on_command(self, mgr, event):

        command = event.command

        ## Start Scan and goto Settings Mode
        if command == FSCommand.SCAN:
            if self._state is FSState.IDLE:
                self.set_state(FSState.SETTINGS)
                self.scanProcessor.tell({FSEvents.COMMAND:FSScanProcessorCommand.SETTINGS_MODE_ON})

        ## Update Settings in Settings Mode
        elif command == FSCommand.UPDATE_SETTINGS:
            if self._state is FSState.SETTINGS:
                self.scanProcessor.tell({FSEvents.COMMAND:FSScanProcessorCommand.UPDATE_SETTINGS, 'SETTINGS': event.settings})

        ## Start Scan Process
        elif command == FSCommand.START:
            if self._state is FSState.SETTINGS:
                self._logger.debug("Start command received...")
                self.set_state(FSState.SCANNING)
                self.scanProcessor.tell({FSEvents.COMMAND:FSScanProcessorCommand.START})

        ## Stop Scan Process or Stop Settings Mode
        elif command == FSCommand.STOP:

            if self._state is FSState.SCANNING:
                self.scanProcessor.ask({FSEvents.COMMAND:FSScanProcessorCommand.STOP})

            if self._state is FSState.SETTINGS:
                self._logger.debug("Close Settings")
                self.scanProcessor.tell({FSEvents.COMMAND:FSScanProcessorCommand.SETTINGS_MODE_OFF})

            self.set_state(FSState.IDLE)

        elif command == FSCommand._COMPLETE:
            self.set_state(FSState.IDLE)
            self._logger.info("Scan complete")

        elif command == FSCommand.SCANNER_ERROR:
            self._logger.info("Internal Scanner Error.")
            self.set_state(FSState.SETTINGS)

        elif command == FSCommand.MESHING:
            meshlab_task = FSMeshlabTask(event.scan_id, event.filter, event.format)
            meshlab_task.start()
            message = FSUtil.new_message()
            message['type'] = FSEvents.ON_INFO_MESSAGE
            message['data']['message'] = "MESHING_STARTED"
            message['data']['level'] = "info"
            self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)

    def on_client_connected(self,eventManager, event):
        message = FSUtil.new_message()
        message['type'] = FSEvents.ON_CLIENT_INIT
        message['data']['client'] = event['client']
        message['data']['state'] = self._state
        message['data']['server_version'] = str(__version__)
        message['data']['firmware_version'] = str(self.hardwareController.get_firmware_version())
        #message['data']['points'] = self.pointcloud
        message['data']['settings'] = self.settings.todict(self.settings)
        eventManager.publish(FSEvents.ON_SOCKET_SEND, message)

        self.scanProcessor.tell({FSEvents.COMMAND:FSScanProcessorCommand.NOTIFY_HARDWARE_STATE})

    def set_state(self, state):
        self._state = state
        message = FSUtil.new_message()
        message['type'] = FSEvents.ON_STATE_CHANGED
        message['data']['state'] = state
        self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)