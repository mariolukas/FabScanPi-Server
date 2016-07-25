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
from fabscan.FSConfig import Config, ConfigInterface, ConfigSingleton
from fabscan.FSSettings import Settings, SettingsInterface
from fabscan.controller import FSHardwareController,FSHardwareControllerInterface, FSHardwareControllerSingleton
from fabscan.FSScanProcessor import FSScanProcessorInterface, FSScanProcessor, FSScanProcessorSingleton
from fabscan.FSVersion import __version__
from fabscan.util.FSInject import injector

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

            # static classes
            injector.provide(FSEventManager, FSEventManager)
            #injector.provide_instance(Config, Config.instance(config=self.config_file))
            #injector.provide_instance(Settings, Settings.instance(settings=self.settings_file))


            # dynamic module classes dependencies... (later this will be plug-ins)
            injector.provide(FSHardwareControllerInterface, FSHardwareController)
            #injector.provide(FSImageProcessor, FSImageProcessor)
            injector.provide(FSScanProcessor, FSScanProcessor)
            injector.provide(ConfigInterface, Config)

            ConfigSingleton(self.config_file)

            self._logger.debug(ConfigSingleton() is ConfigSingleton())
            #self._logger.debug(FSHardwareControllerSingleton() is FSHardwareControllerSingleton())
            #self._logger.debug(FSScanProcessorSingleton() is FSScanProcessorSingleton())

            # Websocket Server
            #FSWebSocketServer().start()
            #FSScanner().start()
            #FSWebServer().start()

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






