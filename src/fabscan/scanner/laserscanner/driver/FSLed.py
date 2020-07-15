__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

class Led:
    def __init__(self, serial_object):
        self.serial_connection = serial_object
        self.is_on = False

    def on(self, red, green, blue):
        if not self.is_on:
            command = "M05 R"+str(red)+" G"+str(green)+" B"+str(blue)
            self.serial_connection.send_and_receive(command)
            # wait for camera to settle
            self.is_on = True

    def off(self):
        if self.is_on:
            command = "M05 R0 G0 B0"
            self.serial_connection.send_and_receive(command)
            self.is_on = False

