__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

class Laser:
    def __init__(self, serial_object):
        self.serial_connection = serial_object

    def on(self, laser=0):
        if (laser != None) and (self.serial_connection != None):
            if laser == 0:
                signal = "M21;"
            else:
                signal = "M19;"

            self.serial_connection.send(signal)
            self.serial_connection.wait_until_ready()

    def off(self, laser=0):
        if (laser != None) and (self.serial_connection != None):
            if laser == 0:
                signal = "M22;"
            else:
                signal = "M20;"

            self.serial_connection.send(signal)
            self.serial_connection.wait_until_ready()

    def turn(self, steps):
        signal = "G04 L"+str(steps)+" F200;"
        self.serial_connection.send(signal)
        self.serial_connection.wait_until_ready()