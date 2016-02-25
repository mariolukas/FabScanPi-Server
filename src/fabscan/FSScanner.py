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
from fabscan.FSScanProcessor import FSScanProcessor
from fabscan.FSSettings import Settings

class FSState(object):
    IDLE = "IDLE"
    SCANNING = "SCANNING"
    SETTINGS = "SETTINGS"

class FSCommand(object):
    SCAN = "SCAN"
    START = "START"
    STOP = "STOP"
    UPDATE_SETTINGS = "UPDATE_SETTINGS"
    _COMPLETE = "_COMPLETE"
    _LASER_DETECTION_FAILED = "_LASER_DETECTION_FAILED"

class FSScanner(threading.Thread):

    def __init__(self):


        threading.Thread.__init__(self)
        self._state = FSState.IDLE
        self._logger =  logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.settings = Settings.instance()
        self.daemon = True
        self.hardwareController = HardwareController.instance()
        self._exit_requested = False

        self._logger.debug("Number of cpu cores: "+str( multiprocessing.cpu_count()))
        self.eventManager = FSEventManager.instance()
        self.eventManager.subscribe(FSEvents.ON_CLIENT_CONNECTED, self._on_client_connected)
        self.eventManager.subscribe(FSEvents.COMMAND, self._on_command)

    def run(self):

        while not self._exit_requested:
            self.eventManager.handle_event_q()

    def request_exit(self):
            self._exit_requested = True

    def _on_command(self,mgr, event):

        command = event.command

        ## Start Scan and goto Settings Mode
        if command == FSCommand.SCAN:
            if self._state is FSState.IDLE:
                self.set_state(FSState.SETTINGS)
                self.hardwareController.settings_mode_on()

        ## Update Settings in Settings Mode
        elif command == FSCommand.UPDATE_SETTINGS:
            if self._state is FSState.SETTINGS:
                try:
                    #self._logger.info(event.settings)
                    self.settings.update(event.settings)
                    self.hardwareController.led.on(self.settings.led.red,self.settings.led.green,self.settings.led.blue)
                except:
                    pass

        ## Start Scan Process
        elif command == FSCommand.START:
            if self._state is FSState.SETTINGS:
                self._logger.debug("Start command received...")
                self.set_state(FSState.SCANNING)
                self.hardwareController.settings_mode_off()
                self.scanProcessor = FSScanProcessor.start()
                self.scanProcessor.tell({FSEvents.COMMAND:FSCommand.START})

        ## Stop Scan Process or Stop Settings Mode
        elif command == FSCommand.STOP:
            if self._state is FSState.SCANNING:
                self.scanProcessor.ask({FSEvents.COMMAND:FSCommand.STOP})
                self.scanProcessor.stop()
                #self.set_state(FSState.IDLE)

            if self._state is FSState.SETTINGS:
                self.hardwareController.settings_mode_off()

            self.set_state(FSState.IDLE)

        elif command == FSCommand._COMPLETE:
            self.set_state(FSState.IDLE)
            self._logger.info("Scan complete")

        elif command == FSCommand._LASER_DETECTION_FAILED:
            #self.scanProcessor.ask({FSEvents.COMMAND:FSCommand.STOP})
            self._logger.info("No Laser detected, returning to settings dialog.")
            #self.scanProcessor.ask({FSEvents.COMMAND:FSCommand.STOP})
            #self.scanProcessor.stop()

            self.set_state(FSState.SETTINGS)
            self.hardwareController.settings_mode_on()


    def _on_client_connected(self,eventManager, event):
        message = FSUtil.new_message()
        message['type'] = FSEvents.ON_CLIENT_INIT
        message['data']['client'] = event['client']
        message['data']['state'] = self._state
        message['data']['server_version'] = str(__version__)
        #message['data']['points'] = self.pointcloud
        message['data']['settings'] = self.settings.todict(self.settings)


        eventManager.publish(FSEvents.ON_SOCKET_SEND, message)

        message = FSUtil.new_message()
        message['type'] = FSEvents.ON_INFO_MESSAGE

        if not self.hardwareController.arduino_is_connected():
            message['data']['message'] = "NO_SERIAL_CONNECTION"
            message['data']['level'] = "error"
        else:
            message['data']['message'] = "SERIAL_CONNECTION_READY"
            message['data']['level'] = "info"

        self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)

        if not self.hardwareController.camera_is_connected():
            message['data']['message'] = "NO_CAMERA_CONNECTION"
            message['data']['level'] = "error"
            self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)
        else:
            message['data']['message'] = "CAMERA_READY"
            message['data']['level'] = "info"

        self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)


    def set_state(self, state):
        self._state = state
        message = FSUtil.new_message()
        message = FSUtil.new_message()
        message['type'] = FSEvents.ON_STATE_CHANGED
        message['data']['state'] = state
        self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)
