__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time
import logging
import sys
import os


from FSWebServer import FSWebServer
from fabscan.FSVersion import __version__
from fabscan.lib.util.FSInject import injector
from fabscan.lib.util.FSUtil import FSSystem, FSSystemExit
from fabscan.FSScanner import FSScanner, FSCommand
from fabscan.FSEvents import FSEventManagerSingleton, FSEventManagerInterface, FSEvents
from fabscan.FSConfig import ConfigInterface, ConfigSingleton, Config
from fabscan.FSSettings import SettingsInterface, SettingsSingleton, Settings
from fabscan.scanner.interfaces import FSScannerFactory
from fabscan.lib.util.FSUpdate import do_upgrade


class FSScanServer(object):
    def __init__(self, args):
        self.system_exit = FSSystemExit()
        self.config_file = args.config
        self.settings_file = args.settings
        self.args = args
        self.exit = False
        self.reboot = False
        self.shutdown = False
        self.scanner = None
        self.webserver = None
        self._logger = logging.getLogger(__name__)

    def on_server_command(self, mgr, event):
        command = event.command

        if command == FSCommand.UPGRADE_SERVER:
            self.upgrade = True
            self.update_server()
            self.restart()

        if command == FSCommand.RESTART_SERVER:
            self.restart = True
            self.restart()

    def restart(self, override_sys=False):
        """Restart the program with params if args is exists"""
        self._logger.debug('argv is: %s' % sys.argv)
        self._logger.debug('args is: %s' % self.args)

        self.exit_services()

        python = sys.executable
        os.execl(python, python, *sys.argv)

    def exit_services(self):
        self.webserver.kill()
        self._logger.debug("Waiting for Webserver exit...")

        self.scanner.kill()
        self._logger.debug("Waiting for Scanner exit...")
        self.scanner.join()

    def create_services(self):
        injector.provide(FSEventManagerInterface, FSEventManagerSingleton)
        injector.provide_instance(ConfigInterface, Config(self.config_file, True))
        injector.provide_instance(SettingsInterface, Settings(self.settings_file, True))

        # inject "dynamic" classes
        self.config = injector.get_instance(ConfigInterface)

        FSScannerFactory.injectScannerType(self.config.scanner_type)

        self.webserver = FSWebServer()
        self.webserver.start()

        self.scanner = FSScanner()
        self.scanner.start()
        FSEventManagerSingleton().instance.subscribe(FSEvents.COMMAND, self.on_server_command)

    def update_server(self):
       try:
         return do_upgrade()
       except StandardError, e:
         self._logger.error(e)

    def run(self):
        self._logger.info("FabScanPi-Server "+str(__version__))

        try:

            self.create_services()

            while not self.system_exit.kill:
                time.sleep(0.3)

            self.exit_services()

            self._logger.info("FabScan Server Exit. Bye!")
            os._exit(1)

        except (KeyboardInterrupt, SystemExit):
            self._logger.info("FabScan Server Exit. Bye!")
            sys.exit(0)
