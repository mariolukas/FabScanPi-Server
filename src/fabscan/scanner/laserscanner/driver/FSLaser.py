__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"
import time

class Laser:
    def __init__(self, serial_object):
        self.serial_connection = serial_object
        self.is_on = [False, False]

    def on(self, laser=0):
        if (laser != None) and (self.serial_connection != None) and not self.is_on[laser]:
            if laser == 0:
                command = "M21;"
            else:
                command = "M19;"

            self.serial_connection.send_and_receive(command)
            # some time until the laser is on.
            # FIXME: The serial needs some time until the laser is turned on.

            self.is_on[laser] = True


    def off(self, laser=0):
        if (laser != None) and (self.serial_connection != None) and self.is_on[laser]:
            if laser == 0:
                command = "M22;"
            else:
                command = "M20;"

            self.serial_connection.send_and_receive(command)
            self.is_on[laser] = False

    def turn(self, steps):
        command = "G04 L"+str(steps)+" F200;"
        self.serial_connection.send_and_receive(command)
