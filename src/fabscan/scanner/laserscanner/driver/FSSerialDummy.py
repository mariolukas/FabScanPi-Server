__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import logging
from fabscan.lib.util.FSInject import inject
from fabscan.FSConfig import ConfigInterface
from fabscan.scanner.interfaces.FSHardwareConnector import FSHardwareConnectorInterface

@inject(
    config=ConfigInterface
)
class FSSerialDummy(FSHardwareConnectorInterface):
    def __init__(self, config):

        self.config = config
        self._logger = logging.getLogger(__name__)
        self._stop = False
        self._connected = False
        self._openSerial()

    def _connect(self):
        self._connected = True
        self._logger.debug("Trying to connect Dummy Connector")
        return

    def _close(self):
        self._connected = False
        self._logger.debug("Dummy Connector closed.")
        return

    def _openSerial(self):
        self._connected = True
        self._logger.debug("Dummy Connector connected.")
        return

    def send_and_receive(self, message):
        self.send(message)
        self._logger.debug("Message Received: {0}".format(message))
        return

    def flush(self):
        pass

    def send(self, message):
        try:
            self._logger.error("Message sent: {0}".format(message))
        except Exception as e:
            self._logger.error("Error while sending: {0}".format(e))

    def is_connected(self):
        return self._connected

    def move_turntable(self, steps, speed, blocking=True):

        gcode = "01"

        if blocking:
            gcode = "02"

        command = "G{0} T{1} F{2}".format(gcode, steps, speed)
        self.send_and_receive(command)
        return

    def laser_on(self, laser):
        if laser == 0:
            command = "M21"
        else:
            command = "M19"
        self.send_and_receive(command)
        return

    def laser_off(self, laser):
        if laser == 0:
            command = "M22"
        else:
            command = "M20"
        self._logger.debug("Laser {0} Switched off".format(laser))
        self.send_and_receive(command)
        return

    def light_on(self, red, green, blue):
        command = "M05 R{0} G{1} B{2}".format(red, green, blue)
        self.send_and_receive(command)
        return

    def light_off(self):
        command = "M05 R0 G0 B0"
        self.send_and_receive(command)
        return
