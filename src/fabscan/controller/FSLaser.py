__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time

class Laser:
    def __init__(self, serial_object):
        self.serial_connection = serial_object

    def on(self, selected_laser=False):
        if (selected_laser != None) and (self.serial_connection != None):

            signal = "M21;"
            self.serial_connection.send(signal+'\n')
            #time.sleep(0.2)
            #self.serial_connection.write("\n".encode('ascii'))
            self.serial_connection.wait()
            time.sleep(0.7)  # Wait for laser to warm up

    def off(self, selected_laser=False):
        if (selected_laser != None) and (self.serial_connection != None):

            signal = "M22;"
            self.serial_connection.send(signal+'\n')
            #time.sleep(0.2)
            #self.serial_connection.write("\n".encode('ascii'))
            self.serial_connection.wait()

    def turn(self, steps):

        signal = "G04 L"+str(steps)+" F200"

        self.serial_connection.send(signal+'\n')
        self.serial_connection.wait()