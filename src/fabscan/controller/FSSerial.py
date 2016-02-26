__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
import glob
import serial
import traceback
import sys
import time
import logging
import subprocess

from fabscan.FSConfig import Config

class FSSerialCom():
    def __init__(self):
        self._logger =  logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.config = Config.instance()
        if hasattr(self.config.serial, 'port'):
            self._port = self.config.serial.port
        else:
            self._port = self._port = self.serialList()[0]
        self._baudrate = self.config.serial.baudrate
        self._serial = None
        self._connected = False
        self._openSerial()


    # Code modified from function serialList obtained from https://github.com/foosel/OctoPrint/blob/master/src/octoprint/util/comm.py
    def serialList(self):
        baselist=[]
        baselist = baselist \
                   + glob.glob("/dev/ttyUSB*") \
                   + glob.glob("/dev/ttyACM*") \
                   + glob.glob("/dev/ttyAMA*") \
                   + glob.glob("/dev/tty.usb*") \
                   + glob.glob("/dev/cu.*") \
                   + glob.glob("/dev/cuaU*") \
                   + glob.glob("/dev/rfcomm*")

        return baselist


    def avr_flash(self,fname):
        status = subprocess.call(["wc -l %s" % (fname)], shell=True)
        status = subprocess.call(["avrdude -U flash:w:%s:i -p atmega328 -b 115200 -carduino -patmega328p -P%s" % (fname,self._port)], shell=True, stdout=subprocess.PIPE)
        if status != 0:
            self._logger.error("Failed to flash firmware")

        return status == 0


    def _connect(self):
        self._logger.debug("Trying to connect Arduino on port: "+str(self._port))
        # open serial port
        try:
            self._serial = serial.Serial(str(self._port), int(self._baudrate), timeout=1)
        except:
            self._logger.error("Could not open serial port")


    def _openSerial(self):

        basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        flash_file_version = max(sorted(glob.iglob(basedir+'/firmware/*.hex'), key=os.path.getctime,reverse=True))
        flash_version_number = os.path.basename(os.path.normpath(os.path.splitext(flash_file_version)[0]))
        self._logger.debug("Latest available firmware version is: "+flash_version_number)

        try:

           # try to connect, if connection works check for firmware...
           self._connect()

           # check if port is open and check if autoflash is set...
           if self._serial.isOpen():

                   current_version = self.checkVersion()

                   self._logger.debug("Installed firmware version: "+current_version)

                   if self.config.serial.autoflash == "True":
                       ## check for curront firmware version
                       if not current_version == flash_version_number:
                           self._logger.info("Old firmare detected trying to flash new firmware...")
                           self.avr_flash(flash_file_version)
                           self._logger.info("FabScan Firmware Version: "+flash_file_version)
                           ## reconnect to new firmware version
                           self._connect()

           # if connection fails, no firmware on device?...
           else:
              if self.config.serial.autoflash == "True":
                    self._logger.info("No firmware detected trying to flash firmware...")
                    self.avr_flash(flash_file_version)
                    self._connect()


           if self._serial.isOpen() and (current_version != "None"):
              self._logger.info("FabScanPi is connected to Arduino or FabScanPi HAT on port: "+str(self._port))
              self._connected = True
           else:
              self._logger.error("Can not find Arduino or FabScanPi HAT")
              self._connected = False

        except:
            ## try to connect for installations where arduino is custom but
            ## autoflash is still active...
            self._connect()
            if self._serial.isOpen():
                self._logger.info("FabScanPi is connected to Arduino")
                self._connected = True
            else:
                self._logger.error("Can not connect to Arduino.")
                self._connected = False


    def checkVersion(self):
        if self._serial:
            self.send("\r\n\r\n")
            time.sleep(2) # Wait for FabScan to initialize
            self._serial.flushInput() # Flush startup text in serial input
            self.send("M200;\n")
            self._serial.readline()
            #self._serial.flushInput()
            value = self._serial.readline()
            value = value.strip()
            if value != "":
                return value
            else:
                return "None"
        else:
            return "None"

    def send(self, message):
        if self._serial:
            self._serial.write(message)

    def flush(self):
       self._serial.flushInput()
       self._serial.flushOutput()

    def wait(self):
        if self._serial:
            value = self._serial.readline()
            self.flush()
            return value

    def is_connected(self):
        return self._connected

