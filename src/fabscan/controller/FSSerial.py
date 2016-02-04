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


try:
	import _winreg
except:
	pass

def getExceptionString():
	locationInfo = traceback.extract_tb(sys.exc_info()[2])[0]
	return "%s: '%s' @ %s:%s:%d" % (str(sys.exc_info()[0].__name__), str(sys.exc_info()[1]), os.path.basename(locationInfo[0]), locationInfo[2], locationInfo[1])


class FSSerialCom():
    def __init__(self):
        self._logger =  logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.config = Config.instance()
        self._port = self.config.serial.port
        self._baudrate = self.config.serial.baudrate
        self._serial = None
        self._openSerial()


    # Code modified from function serialList obtained from https://github.com/foosel/OctoPrint/blob/master/src/octoprint/util/comm.py
    def serialList(self):
        baselist=[]
        if os.name=="nt":
            try:
                key=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"HARDWARE\\DEVICEMAP\\SERIALCOMM")
                i=0
                while(1):
                    baselist+=[_winreg.EnumValue(key,i)[1]]
                    i+=1
            except:
                pass
        baselist = baselist \
                   + glob.glob("/dev/ttyUSB*") \
                   + glob.glob("/dev/ttyACM*") \
                   + glob.glob("/dev/ttyAMA*") \
                   + glob.glob("/dev/tty.usb*") \
                   + glob.glob("/dev/cu.*") \
                   + glob.glob("/dev/cuaU*") \
                   + glob.glob("/dev/rfcomm*")

        #additionalPorts = config().serial.port
        #for additional in additionalPorts:
        #    baselist += glob.glob(additional)

        prev = self.config.serial.port
        if prev in baselist:
            baselist.remove(prev)
            baselist.insert(0, prev)
#        if bool(config().serial.virtual)
#            baselist.append("VIRTUAL")
        return baselist


    # Code modified from function baudrateList obtained from https://github.com/foosel/OctoPrint/blob/master/src/octoprint/util/comm.py
    def baudrateList(self):
        ret = [250000, 230400, 115200, 57600, 38400, 19200, 9600]
        prev = self.config.serial.port
        if prev in ret:
            ret.remove(prev)
            ret.insert(0, prev)
        return ret

    def avr_flash(self,fname):
        status = subprocess.call(["wc -l %s" % (fname)], shell=True)
        status = subprocess.call(["avrdude -U flash:w:%s:i -p atmega328 -b 115200 -carduino -patmega328p -P%s" % (fname,self.config.serial.port)], shell=True, stdout=subprocess.PIPE)

        if status != 0:
            self._logger.error("Failed to flash firmware")
        return status == 0

    def receiving(self):
        global last_received

        buffer_string = ''
        while True:
            buffer_string = buffer_string + self._serial.read(self._serial.inWaiting())
            if '\n' in buffer_string:
                lines = buffer_string.split('\n') # Guaranteed to have at least 2 entries
                last_received = lines[-2]
                #If the Arduino sends lots of empty lines, you'll lose the
                #last filled line, so you could make the above statement conditional
                #like so: if lines[-2]: last_received = lines[-2]
                buffer_string = lines[-1]

        print buffer_string



    def _connect(self):
        '''Serial communications: get a response'''

        # open serial port
        try:
            self._serial = serial.Serial(str(self._port), int(self._baudrate), timeout=1)

        except self._serial.SerialException as e:
            self._logger.error("could not open serial port '{}': {}".format(str(self._port), e))




    def _openSerial(self):
        basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


        flash_file_version = max(glob.iglob(basedir+'/firmware/*.[Hh][Ee][Xx]'), key=os.path.getctime)
        flash_version_number = os.path.basename(os.path.normpath(os.path.splitext(flash_file_version)[0]))


        self._logger.debug("Found Firmware Version: "+flash_version_number)


        try:

           self._connect()

           if self.config.serial.autoflash == "True":
               current_version = self.checkVersion()
               if not current_version == flash_version_number:
                   self._logger.info("Flashing new Firmware...")
                   self.avr_flash(flash_file_version)
                   self._logger.info("FabScan Firmware Version: "+flash_file_version)
                   self._connect()
               else:
                   self._logger.info("FabScan is using Firmware Version: "+current_version)
                   self._connect()

        except:

            if flash_file_version:
                self._logger.info("Connection failed trying to flash Firmware...")
                #self.avr_flash(basedir+"/firmware/"+flash_file_version+".hex")
                self._logger.info("FabScan Firmware Version: "+flash_file_version)
            else:
                self._logger.error("No firmware file found.")
            try:
                self._logger.debug("Trying to connect ... ")
                self._connect()
            except:
                self._logger.exception("Serial Connection Error.")

            self._logger.debug("abbort")


    def checkVersion(self):
        if self._serial:
            self.send("\r\n\r\n")
            time.sleep(2) # Wait for open exposer to initialize
            self._serial.flushInput() # Flush startup text in serial input
            self.send("M200;\n")
            self._serial.readline()
            #self._serial.flushInput()
            value = self._serial.readline()
            value = value.strip()
            return value
        else:
            return 0

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


