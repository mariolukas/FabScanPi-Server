__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time
import logging
import sys

from WebServer import FSWebServer
from fabscan.FSVersion import __version__
from fabscan.util.FSInject import injector
from fabscan.server.websockets import FSWebSocketServer, FSWebSocketServerInterface
from fabscan.FSScanner import FSScanner
from fabscan.FSEvents import FSEventManager, FSEventManagerSingleton, FSEventManagerInterface
from fabscan.FSConfig import ConfigInterface, ConfigSingleton
from fabscan.FSSettings import SettingsInterface, SettingsSingleton
from fabscan.FSScanProcessor import FSScanProcessorInterface, FSScanProcessorSingleton
from fabscan.controller import FSHardwareControllerSingleton, FSHardwareControllerInterface
from fabscan.vision.FSImageProcessor import ImageProcessor, ImageProcessorInterface


class FSServer(object):
    def __init__(self,config_file, settings_file):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        self.config_file = config_file
        self.settings_file = settings_file

    def run(self):
        self._logger.info("FabScanPi-Server "+str(__version__))

        try:
            # "static" classes
            injector.provide(FSEventManagerInterface, FSEventManager)
            injector.provide(FSWebSocketServerInterface, FSWebSocketServer)
            injector.provide_instance(ConfigInterface, ConfigSingleton(self.config_file))
            injector.provide_instance(SettingsInterface, SettingsSingleton(self.settings_file))

            # "dynamic" module classes ... (later called plug-ins/scan-modules)
            injector.provide(ImageProcessorInterface, ImageProcessor)
            injector.provide(FSHardwareControllerInterface, FSHardwareControllerSingleton)
            injector.provide(FSScanProcessorInterface, FSScanProcessorSingleton)

            FSWebSocketServer().start()
            FSWebServer().start()
            FSScanner().start()

            while True:
                try:
                    time.sleep(0.3)
                except KeyboardInterrupt:
                    raise


        except (KeyboardInterrupt, SystemExit):
            sys.exit(0)






