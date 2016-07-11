__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time
import threading
import logging
import multiprocessing
import traceback

from fabscan.FSVersion import __version__
from fabscan.FSEvents import FSEventManager, FSEvents
from fabscan.hardware.FSHardwareControllerFactory import FSHardwareControllerFactory
from fabscan.scanner.FSScanProcessorFactory import FSScanProcessorFactory
from fabscan.scanner.FSAbstractScanProcessor import FSScanProcessorCommand
from fabscan.vision.FSMeshlabProcessor import FSMeshlabTask
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
    MESHING = "MESHING"
    COMPLETE = "COMPLETE"
    SCANNER_ERROR = "SCANNER_ERROR"


class FSScanner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._state = FSState.IDLE
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.settings = Settings.instance()
        self.daemon = True
        self._exit_requested = False
        self.meshingTaskRunning = False
        self.scanProcessor = FSScanProcessorFactory.get_scanner_obj("laser")
        self._logger.debug("Number of cpu cores: " + str(multiprocessing.cpu_count()))
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
                try:
                    self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.SETTINGS_MODE_ON})
                except Exception as e:
                    stack_trace = traceback.format_exc()
                    self._logger.error(stack_trace)

        ## Update Settings in Settings Mode
        elif command == FSCommand.UPDATE_SETTINGS:
            if self._state is FSState.SETTINGS:
                self.scanProcessor.tell(
                        {FSEvents.COMMAND: FSScanProcessorCommand.UPDATE_SETTINGS, 'SETTINGS': event.settings})

        ## Start Scan Process
        elif command == FSCommand.START:
            if self._state is FSState.SETTINGS:
                self._logger.debug("Start command received...")
                self.set_state(FSState.SCANNING)
                self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.START})

        ## Stop Scan Process or Stop Settings Mode
        elif command == FSCommand.STOP:

            if self._state is FSState.SCANNING:
                self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.STOP})

            if self._state is FSState.SETTINGS:
                self._logger.debug("Close Settings")
                self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.SETTINGS_MODE_OFF})

            self.set_state(FSState.IDLE)

        elif command == FSCommand.COMPLETE:
            self.set_state(FSState.IDLE)
            self._logger.info("Scan complete")

        elif command == FSCommand.SCANNER_ERROR:
            self._logger.info("Internal Scanner Error.")
            self.set_state(FSState.SETTINGS)

        elif command == FSCommand.MESHING:
            meshlab_task = FSMeshlabTask(event.scan_id, event.filter, event.format)
            meshlab_task.start()

    def on_client_connected(self, eventManager, event):

        hardware_info = self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.GET_HARDWARE_INFO})
        
        message = {
            "client": event['client'],
            "state": self._state,
            "server_version": str(__version__),
            "firmware_version": hardware_info,
            "settings": self.settings.todict(self.settings)
        }

        eventManager.send_client_message(FSEvents.ON_CLIENT_INIT, message)
        try:
            self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.NOTIFY_HARDWARE_STATE})
        except Exception as e:
            stack_trace = traceback.format_exc()
            self._logger.error(stack_trace)

    def set_state(self, state):
        self._state = state
        self.eventManager.broadcast_client_message(FSEvents.ON_STATE_CHANGED, {'state': state})
