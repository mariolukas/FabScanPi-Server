__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time
import threading
import logging
import os
import multiprocessing
from apscheduler.schedulers.background import BackgroundScheduler

from fabscan.FSVersion import __version__

from fabscan.FSEvents import FSEventManagerInterface, FSEvents
from fabscan.worker.FSMeshlab import FSMeshlabTask
from fabscan.FSSettings import SettingsInterface
from fabscan.FSConfig import ConfigInterface
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorCommand, FSScanProcessorInterface
from fabscan.lib.util.FSInject import inject
from fabscan.lib.util.FSUpdate import upgrade_is_available, do_upgrade
from fabscan.lib.util.FSDiscovery import register_to_discovery
from fabscan.lib.util.FSSystemWatch import get_cpu_temperature

class FSState(object):
    IDLE = "IDLE"
    SCANNING = "SCANNING"
    SETTINGS = "SETTINGS"
    CONFIG = "CONFIG"
    CALIBRATING = "CALIBRATING"
    UPGRADING = "UPGRADING"

class FSCommand(object):
    SCAN = "SCAN"
    START = "START"
    STOP = "STOP"
    CONFIG_MODE_ON = "CONFIG_MODE_ON"
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
        scanprocessor=FSScanProcessorInterface,
)
class FSScanner(threading.Thread):
    def __init__(self, settings, config, eventmanager, scanprocessor):
        threading.Thread.__init__(self)

        self._logger = logging.getLogger(__name__)
        self.settings = settings
        self.config = config
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
        self._logger.info("Number of cpu cores: {0}".format(multiprocessing.cpu_count()))
        self.config = config

        if bool(self.config.file.discoverable):
            self.run_discovery_service()
            self.scheduler.add_job(self.run_discovery_service, 'interval', minutes=30, id='register_discovery_service')
            self._logger.info("Added discovery scheduling job.")

        self.scheduler.add_job(self.run_temperature_watch_service, 'interval', minutes=1, id='cpu_temperature_service')

    def run(self):
        while not self.exit:
            time.sleep(0.2)

    def kill(self):
        self.scanProcessor.stop()
        self.scheduler.shutdown()
        # wait some time for hardware shutdown
        time.sleep(1)
        self.exit = True


    def on_command(self, mgr, event):

        command = event.command

        ## Start Scan and goto Settings Mode
        if command == FSCommand.SCAN:
            if self._state is FSState.IDLE:
                self.set_state(FSState.SETTINGS)
                self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.SETTINGS_MODE_ON})
                return

        ## Update Settings in Settings Mode
        elif command == FSCommand.UPDATE_SETTINGS:
            if self._state is FSState.SETTINGS:
                self.scanProcessor.tell(
                    {FSEvents.COMMAND: FSScanProcessorCommand.UPDATE_SETTINGS, 'SETTINGS': event.settings}
                )
                return

        elif command == FSCommand.UPDATE_CONFIG:
            self.scanProcessor.tell(
                {FSEvents.COMMAND: FSScanProcessorCommand.UPDATE_CONFIG, 'CONFIG': event.config}
            )
            return

        ## Start Scan Process
        elif command == FSCommand.START:
            if self._state is FSState.SETTINGS:
                self._logger.info("Start command received...")
                self.set_state(FSState.SCANNING)
                self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.START})
                return

        elif command == FSCommand.CONFIG_MODE_ON:
            if self._state is FSState.IDLE:
                self._logger.info("Config mode command received...")
                self.set_state(FSState.CONFIG)
                self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.CONFIG_MODE_ON})
                return

        ## Stop Scan Process or Stop Settings Mode
        elif command == FSCommand.STOP:

            if self._state is FSState.CONFIG:
                self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.CONFIG_MODE_OFF})
                if not (self._state is FSState.CALIBRATING):
                    self.set_state(FSState.IDLE)
                return

            if self._state is FSState.SCANNING:
                self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.STOP})
                self.eventManager.publish(FSEvents.ON_STOP_MJPEG_STREAM, "STOP_IT")
                self.set_state(FSState.IDLE)
                return

            if self._state is FSState.SETTINGS:
                self._logger.debug("Close Settings")
                self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.SETTINGS_MODE_OFF})
                self.eventManager.publish(FSEvents.ON_STOP_MJPEG_STREAM, "STOP_IT")
                self.set_state(FSState.IDLE)
                return

            if self._state is FSState.CALIBRATING:
                self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.STOP_CALIBRATION})
                self.eventManager.publish(FSEvents.ON_STOP_MJPEG_STREAM, "STOP_IT")
                self.set_state(FSState.IDLE)
                return

        elif command == FSCommand.HARDWARE_TEST_FUNCTION:
            self._logger.debug("Hardware Device Function called...")
            self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.CALL_HARDWARE_TEST_FUNCTION, 'DEVICE_TEST': event.device})
            return

        # Start calibration
        elif command == FSCommand.CALIBRATE:
            self.set_state(FSState.CALIBRATING)
            self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.START_CALIBRATION})
            return

        elif command == FSCommand.CALIBRATION_COMPLETE:
            self.set_state(FSState.IDLE)
            return

        # Scan is complete
        elif command == FSCommand.COMPLETE:
            self.set_state(FSState.IDLE)
            self._logger.info("Scan complete")
            return

        # Internal error occured
        elif command == FSCommand.SCANNER_ERROR:
            self._logger.info("Internal Scanner Error.")
            self.set_state(FSState.SETTINGS)
            return

        # Meshing
        elif command == FSCommand.MESHING:
            meshlab_task = FSMeshlabTask(event.scan_id, event.filter, event.format, event.file)
            meshlab_task.start()
            return

        elif command == FSCommand.HARDWARE_TEST_FUNCTION:
            self._logger.debug("Hardware Device Function called...")
            self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.CALL_HARDWARE_TEST_FUNCTION, 'DEVICE_TEST': event.device})
            return

        # Upgrade server
        elif command == FSCommand.UPGRADE_SERVER:
            if self._upgrade_available:
                self._logger.info("Started Server upgrade...")
                self.set_state(FSState.UPGRADING)
                return

        elif command == FSCommand.GET_CONFIG:
            message = {
                "client": event['client'],
                "config": self.config.file
            }
            self.eventManager.send_client_message(FSEvents.ON_GET_CONFIG, message)
            return

        elif command == FSCommand.GET_SETTINGS:
            message = {
                "client": event['client'],
                "settings": self.settings.file
            }
            self.eventManager.send_client_message(FSEvents.ON_GET_SETTINGS, message)
            return


    def on_client_connected(self, eventManager, event):
        try:
            try:
                hardware_info = self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.GET_HARDWARE_INFO})
            except:
                hardware_info = "undefined"

            self._upgrade_available, self._upgrade_version = upgrade_is_available(__version__, self.config.file.online_lookup_ip)
            self._logger.debug("Upgrade available: {0} {1}".format(self._upgrade_available, self._upgrade_version))

            #FIXME: todict leads to too many recursion problems. refactor settings class
            message = {
                "client": event['client'],
                "state": self.get_state(),
                "server_version": 'v.'+__version__,
                "firmware_version": str(hardware_info),
                "settings": self.settings.file,
                "upgrade": {
                    "available": self._upgrade_available,
                    "version": self._upgrade_version
                }
            }

            eventManager.send_client_message(FSEvents.ON_CLIENT_INIT, message)
            self.scanProcessor.tell({FSEvents.COMMAND: FSScanProcessorCommand.NOTIFY_HARDWARE_STATE})

        except Exception as e:
            self._logger.exception("Client Connection Error: {0}".format(e))

    def set_state(self, state):
        self._state = state

        self.eventManager.broadcast_client_message(FSEvents.ON_STATE_CHANGED, {'state': state})

    def get_state(self):
        return self._state

    ## Scheduled functions see init function!!
    def run_temperature_watch_service(self):
        cpu_temp = get_cpu_temperature()
        if cpu_temp > 82:
            self._logger.warning("High CPU Temperature: {0} C".format(cpu_temp))
            message = {
                "message": "CPU Temp: {0} C! Maybe thermally throttle active.".format(cpu_temp),
                "level": "warn"
            }

            self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        else:
            self._logger.debug("CPU Temperature: {0} C".format(cpu_temp))

    def run_discovery_service(self):
        try:
            hardware_info = self.scanProcessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.GET_HARDWARE_INFO})
        except:
            hardware_info = "undefined"

        register_to_discovery(str(__version__), str(hardware_info))
