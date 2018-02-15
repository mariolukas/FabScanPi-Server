__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"
import time

class Led:
    def __init__(self, serial_object):
        self.serial_connection = serial_object

    def on(self, red, green, blue):
            command = "M05 R"+str(red)+" G"+str(green)+" B"+str(blue)+";"
            self.serial_connection.send_and_receive(command)

    def off(self):
            command = "M05 R0 G0 B0;"
            self.serial_connection.send_and_receive(command)

