__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time
import logging
import sys
import os
import threading
from WebServer import FSWebServer
from fabscan.FSVersion import __version__
from fabscan.util.FSInject import injector
from fabscan.util.FSUtil import FSSystem
from fabscan.server.websockets import FSWebSocketServer, FSWebSocketServerInterface
from fabscan.FSScanner import FSScanner, FSCommand
from fabscan.FSEvents import FSEventManagerSingleton, FSEventManagerInterface, FSEvents
from fabscan.FSConfig import ConfigInterface, ConfigSingleton, Config
from fabscan.FSSettings import SettingsInterface, SettingsSingleton, Settings
from fabscan.FSScanProcessor import FSScanProcessorInterface, FSScanProcessorSingleton
from fabscan.controller import FSHardwareControllerSingleton, FSHardwareControllerInterface
from fabscan.vision.FSImageProcessor import ImageProcessor, ImageProcessorInterface


class FSServer(object):
    def __init__(self,config_file, settings_file):

        self.config_file = config_file
        self.settings_file = settings_file
        self.exit = False
        self.restart = False
        self.upgrade = False
        self._logger = logging.getLogger(__name__)

        self._logger.debug(self.config_file)

    def on_server_command(self, mgr, event):
        command = event.command

        if command == FSCommand.UPGRADE_SERVER:
            self.exit = True
            self.upgrade = True

        if command == FSCommand.RESTART_SERVER:
            self.exit = True
            self.restart = True


    def restart_server(self):
        try:
            FSSystem.run_command("/etc/init.d/fabscanpi-server restart", blocking=True)
        except StandardError, e:
            self._logger.error(e)

    def update_server(self):
         try:
            FSSystem.run_command("apt-get update")
            FSSystem.run_command("nohup apt-get -y --only-upgrade install fabscanpi-server")
         except StandardError, e:
            self._logger.error(e)


    def run(self):
        self._logger.info("FabScanPi-Server "+str(__version__))

        try:
            # "static" classes
            injector.provide(FSEventManagerInterface, FSEventManagerSingleton)
            injector.provide(FSWebSocketServerInterface, FSWebSocketServer)
            injector.provide_instance(ConfigInterface, Config(self.config_file, True))
            injector.provide_instance(SettingsInterface, Settings(self.settings_file, True))

            # "dynamic" module classes ... (later called plug-ins/scan-modules)
            injector.provide(ImageProcessorInterface, ImageProcessor)
            injector.provide(FSHardwareControllerInterface, FSHardwareControllerSingleton)
            injector.provide(FSScanProcessorInterface, FSScanProcessorSingleton)

            FSWebSocketServer().start()
            FSWebServer().start()
            FSScanner().start()

            FSEventManagerSingleton().instance.subscribe(FSEvents.COMMAND, self.on_server_command)

            while not self.exit:
                try:
                    time.sleep(0.3)

                except KeyboardInterrupt:
                    raise

            if self.upgrade:
                self._logger.info("Upgrading FabScanPi Server")
                self.update_server()
                self.restart = True

            if self.restart:
                self._logger.info("Restarting FabScanPi Server")
                self.restart_server()
                self.exit = True

            self._logger.info("FabScan Server Exit. Bye!")
            os._exit(1)

        except (KeyboardInterrupt, SystemExit):
            sys.exit(0)






