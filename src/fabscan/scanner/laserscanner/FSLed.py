__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"
import time

class Led:
    def __init__(self, serial_object):
        self.serial_connection = serial_object

    def on(self, red, green, blue):

            signal = "M05 R"+str(red)+" G"+str(green)+" B"+str(blue)+";"
            self.serial_connection.send(signal+'\n')
            time.sleep(0.7)
            #self.serial_connection.write("\n".encode('ascii'))
            self.serial_connection.wait()

    def off(self):
            signal = "M05 R0 G0 B0;"
            self.serial_connection.send(signal+'\n')
            time.sleep(0.7)
            #self.serial_connection.write("\n".encode('ascii'))
            self.serial_connection.wait()
