__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time
import threading
import logging
import multiprocessing
from apscheduler.schedulers.background import BackgroundScheduler

from fabscan.FSVersion import __version__

from fabscan.FSEvents import FSEventManagerInterface, FSEvents
from fabscan.worker.FSMeshlab import FSMeshlabTask
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorCommand, FSScanProcessorInterface
from fabscan.lib.util.FSInject import inject, singleton
from fabscan.lib.util.FSUpdate import upgrade_is_available, do_upgrade
from fabscan.lib.util.FSDiscovery import register_to_discovery

class FSState(object):
    IDLE = "IDLE"
    SCANNING = "SCANNING"
    SETTINGS = "SETTINGS"
    CALIBRATING = "CALIBRATING"
    UPGRADING = "UPGRADING"

class FSCommand(object):
    SCAN = "SCAN"
    START = "START"
    STOP = "STOP"
    CALIBRATE = "CALIBRATE"
    HARDWARE_TEST_FUNCTION = "HARDWARE_TEST_FUNCTION"
    MESHING = "MESHING"
    COMPLETE = "COMPLETE"
    SCANNER_ERROR = "SCANNER_ERROR"
    UPGRADE_SERVER = "UPGRADE_SERVER"
    RESTART_SERVER = "RESTART_SERVER"
    REBOOT_SYSTEM = "REBOOT_SYSTEM"
    SHUTDOWN_SYSTEM = "SHUTDOWN_SYSTEM"
    CALIBRATION_COMPLETE = "CALIBRATION_COMPLETE"
    NETCONNECT = "NETCONNECT"
    GET_SETTINGS = "GET_SETTINGS"
    UPDATE_SETTINGS = "UPDATE_SETTINGS"
    GET_CONFIG = "GET_CONFIG"
    UPDATE_CONFIG = "UPDATE_CONFIG"


@inject(
        settings=SettingsInterface,
        config=ConfigInterface,
        eventmanager=FSEventManagerInterface,
        scanprocessor=FSScanProcessorInterface
)
class FSScanner(threading.Thread):
    def __init__(self, settings, config, eventmanager, scanprocessor):
        threading.Thread.__init__(self)

        self._logger = logging.getLogger(__name__)
        self.settings = settings
        self.eventManager = eventmanager.instance
        self.scanProcessor = scanprocessor.start()

        self._state = FSState.IDLE
        self.exit = False
        self.meshingTaskRunning = False

        self._upgrade_available = False
        self._update_version = None

        self.eventManager.subscribe(FSEvents.ON_CLIENT_CONNECTED, self.on_client_connected)
        self.eventManager.subscribe(FSEvents.COMMAND, self.on_command)

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self._logger.info("Job scheduler started.")

        self._logger.info("Scanner initialized...")
        self._logger.info("Number of cpu cores: " + str(multiprocessing.cpu_count()))
        self.config = config

        if self.config.register_as_discoverable == 'True':
           self.run_discovery_service()
           self.scheduler.add_job(self.run_discovery_service, 'interval', minutes=30, id='register_discovery_service')
           self._logger.info("Added discovery scheduling job.")

    def run(self):
        while not self.exit:
            self.eventManager.handle_event_q()
            time.sleep(0.05)

        self.scanProcessor.stop()


    def kill(self):
        self.exit = True


    def on_command(self, mgr, event):

        command = event.command

        ## Start Scan and goto Settings Mode
        if command == FSCommand.SCAN:
            if self._state is FSState.IDLE:
                self.set_state(FSState.SETTINGS)
                self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.SETTINGS_MODE_ON})

        ## Update Settings in Settings Mode
        elif command == FSCommand.UPDATE_SETTINGS:
            if self._state is FSState.SETTINGS:
                self.scanProcessor.tell(
                        {FSEvents.COMMAND: FSScanProcessorCommand.UPDATE_SETTINGS, 'SETTINGS': event.settings})

        ## Start Scan Process
        elif command == FSCommand.START:
            if self._state is FSState.SETTINGS:
                self._logger.info("Start command received...")
                self.set_state(FSState.SCANNING)
                self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.START})

        ## Stop Scan Process or Stop Settings Mode
        elif command == FSCommand.STOP:
            if self._state is FSState.SCANNING:
                self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.STOP})

            if self._state is FSState.SETTINGS:
                self._logger.debug("Close Settings")
                self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.SETTINGS_MODE_OFF})

            if self._state is FSState.CALIBRATING:
                self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.STOP_CALIBRATION})

            self.set_state(FSState.IDLE)

        # Start calibration
        elif command == FSCommand.CALIBRATE:
            self._logger.debug("Calibration started....")
            self.set_state(FSState.CALIBRATING)
            self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.START_CALIBRATION})

        elif command == FSCommand.CALIBRATION_COMPLETE:
            self.set_state(FSState.IDLE)

        # Scan is complete
        elif command == FSCommand.COMPLETE:
            self.set_state(FSState.IDLE)
            self._logger.info("Scan complete")

        # Internal error occured
        elif command == FSCommand.SCANNER_ERROR:
            self._logger.info("Internal Scanner Error.")
            self.set_state(FSState.SETTINGS)

        # Meshing
        elif command == FSCommand.MESHING:
            meshlab_task = FSMeshlabTask(event.scan_id, event.filter, event.format)
            meshlab_task.start()

        # Upgrade server
        elif command == FSCommand.UPGRADE_SERVER:
            if self._upgrade_available:
                self._logger.info("Upgrade server")
                self.set_state(FSState.UPGRADING)


    # new client conneted
    def on_client_connected(self, eventManager, event):
        try:
            try:
                hardware_info = self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.GET_HARDWARE_INFO})
            except:
                hardware_info = "undefined"

            self._upgrade_available, self._upgrade_version = upgrade_is_available(__version__)
            self._logger.debug("Upgrade available: "+str(self._upgrade_available)+" "+self._upgrade_version)

            message = {
                "client": event['client'],
                "state": self.get_state(),
                "server_version": 'v.'+__version__,
                "firmware_version": str(hardware_info),
                "settings": self.settings.todict(self.settings),
                "upgrade": {
                    "available": self._upgrade_available,
                    "version": self._upgrade_version
                }
            }


            eventManager.send_client_message(FSEvents.ON_CLIENT_INIT, message)
            self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.NOTIFY_HARDWARE_STATE})
            #self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.NOTIFY_IF_NOT_CALIBRATED})

        except StandardError, e:
            self._logger.error(e)

    def set_state(self, state):
        self._state = state
        self.eventManager.broadcast_client_message(FSEvents.ON_STATE_CHANGED, {'state': state})

    def get_state(self):
        return self._state

    def run_discovery_service(self):

        try:
            hardware_info = self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.GET_HARDWARE_INFO})
        except:
            hardware_info = "undefined"

        register_to_discovery(str(__version__), str(hardware_info))
