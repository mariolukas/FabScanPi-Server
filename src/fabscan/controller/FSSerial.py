__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
import glob
import serial
import time
import logging
from fabscan.util.FSUtil import FSSystem

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
        self._firmware_version = None
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


    def avr_device_is_available(self):
        status = FSSystem.run_command("avrdude -p m328p -b 57600 -carduino -P"+str(self._port))
        return status == 0

    def avr_flash(self,fname):
        FSSystem.run_command("wc -l "+str(fname))
        status = FSSystem.run_command("avrdude -D -V -U flash:w:"+str(fname)+":i -b 57600 -carduino -pm328p -P"+str(self._port))
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

    def _close(self):
        self._serial.close()


    def _openSerial(self):

        basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        flash_file_version = max(sorted(glob.iglob(basedir+'/firmware/*.hex'), key=os.path.getctime,reverse=True))
        flash_version_number = os.path.basename(os.path.normpath(os.path.splitext(flash_file_version)[0]))
        self._logger.debug("Latest available firmware version is: "+flash_version_number)

        try:
           # check if device is available
           if self.avr_device_is_available():
                   time.sleep(0.5)
                   # try to connect to arduino
                   self._connect()

                   # if connection is opened successfully
                   if self._serial.isOpen():
                           current_version = self.checkVersion()
                           self._logger.debug("Installed firmware version: "+current_version)
                           # check if autoflash is active
                           if self.config.serial.autoflash == "True":
                               ## check if firmware is up to date, if not flash new firmware
                               if not current_version == flash_version_number:
                                   self._close()
                                   self._logger.info("Old firmare detected trying to flash new firmware...")
                                   if self.avr_flash(flash_file_version):
                                        time.sleep(0.5)
                                        self._connect()
                                        current_version = self.checkVersion()
                                        self._logger.info("Successfully flashed new Firmware Version: "+current_version)


                   # no firmware is installed, flash firmware
                   else:
                            # if auto flash is activated
                            if self.config.serial.autoflash == "True":
                                    self._logger.info("No firmware detected trying to flash firmware...")
                                    if self.avr_flash(flash_file_version):
                                        time.sleep(0.5)
                                        self._connect()
                                        current_version = self.checkVersion()
                                        self._logger.info("Successfully flashed Firmware Version: "+current_version)
           else:
                    self._logger.error("No Arduino compatible device found on port "+str(self._port))

           # set connection states and version
           if self._serial.isOpen() and (current_version != "None"):
                  self._logger.info("FabScanPi is connected to Arduino or FabScanPi HAT on port: "+str(self._port))
                  current_version = self.checkVersion()
                  self._firmware_version = current_version
                  self._connected = True
           else:
                  self._logger.error("Can not find Arduino or FabScanPi HAT")
                  self._connected = False

        except:
            self._logger.error("Fatal Arduino connection error....")


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

    def get_firmware_version(self):
        return self._firmware_version