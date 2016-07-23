__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time
import logging
import sys
from WebServer import FSWebServer

from fabscan.server.websockets import FSWebSocketServer
from fabscan.FSScanner import FSScanner
from fabscan.FSEvents import FSEventManager
from fabscan.FSConfig import Config, FSConfigInterface
from fabscan.FSSettings import Settings
from fabscan.controller import FSHardwareController
from fabscan.FSScanProcessor import FSScanProcessor
from fabscan.FSVersion import __version__
from fabscan.util.FSInject import injector
import threading


class FSServer():
    def __init__(self,config_file, settings_file):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.hardwareController = None
        self.config_file = config_file
        self.settings_file = settings_file

    def run(self):
        self._logger.info("FabScanPi-Server "+str(__version__))

        try:
            # dynamic module classes dependencies... (later this will be plug-ins)
            injector.provide(FSHardwareController, FSHardwareController)
            #injector.provide(FSImageProcessor, FSImageProcessor)
            injector.provide(FSScanProcessor, FSScanProcessor)

            # static classes
            injector.provide(FSEventManager, FSEventManager)
            injector.provide_instance(Config, Config.instance(self.config_file))
            injector.provide_instance(Settings, Settings.instance(self.settings_file))

            # Websocket Server
            FSWebSocketServer().start()
            FSScanner().start()
            FSWebServer().start()

            while True:
                try:
                    time.sleep(0.3)
                except KeyboardInterrupt:
                    raise


        except (KeyboardInterrupt, SystemExit):

            time.sleep(0.5)
            #_hardwareController.laser.off()
            #_hardwareController.led.off()
            #_hardwareController.turntable.stop_turning()
            pass
            #sys.exit(0)






