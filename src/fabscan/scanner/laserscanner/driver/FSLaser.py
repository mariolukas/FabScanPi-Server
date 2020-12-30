__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"
import time

class Laser:
    def __init__(self, hardware_connector):
        self.hardware_connector = hardware_connector
        self.is_on = [False, False]

    def on(self, laser=0):
        if (laser != None) and (self.hardware_connector != None) and not self.is_on[laser]:
            self.hardware_connector.laser_on(laser)
            time.sleep(0.4)
            self.is_on[laser] = True

    def off(self, laser=0):
        if (laser != None) and (self.hardware_connector != None) and self.is_on[laser]:
            self.hardware_connector.laser_off(laser)
            self.is_on[laser] = False
