__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

class Led:
    def __init__(self, serial_object):
        self.serial_connection = serial_object

    def on(self, red, green, blue):

            signal = "M05 R"+str(red)+" G"+str(green)+" B"+str(blue)+";"
            self.serial_connection.send(signal+'\n')

            #self.serial_connection.write("\n".encode('ascii'))
            #wait_serial(self.serial_connection)

    def off(self):
            signal = "M05 R0 G0 B0;"
            self.serial_connection.send(signal+'\n')

            #self.serial_connection.write("\n".encode('ascii'))
            #wait_serial(self.serial_connection)
