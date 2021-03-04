__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
import glob
import serial
import time
import sys
import logging
from fabscan.lib.util.FSUtil import FSSystem
from fabscan.lib.util.FSInject import inject
from fabscan.FSConfig import ConfigInterface
from fabscan.scanner.interfaces.FSHardwareConnector import FSHardwareConnectorInterface

@inject(
    config=ConfigInterface
)
class FSSerialCom(FSHardwareConnectorInterface):
    def __init__(self, config):

        self.config = config
        self._logger = logging.getLogger(__name__)

        if hasattr(self.config.file.connector, 'port'):
            self._port = self.config.file.connector.port
            self._logger.debug("Port in Config found using: {0}".format(self._port))
        else:
            self._port = "/dev/ttyAMA0"

        if hasattr(self.config.file.connector, 'flash_baudrate'):
            self.flash_baudrate = self.config.file.connector.flash_baudrate
        else:
            self.flash_baudrate = 57600

        self.buf = bytearray()

        self._baudrate = self.config.file.connector.baudrate
        self._serial = None
        self._connected = False
        self._firmware_version = None
        self._openSerial()
        self._logger.debug("Connection baudrate is: {0}".format(self._baudrate))
        self._logger.debug("Firmware flashing baudrate is: {0}".format(self.flash_baudrate))

        self._stop = False

    def avr_device_is_available(self):
        status = FSSystem.run_command("sudo avrdude-autoreset -p m328p -b {0} -carduino -P{1}".format(self.flash_baudrate, self._port))
        return status == 0

    def avr_flash(self, fname):
        FSSystem.run_command("wc -l {0}".format(fname))
        status = FSSystem.run_command("sudo avrdude-autoreset -D -V -U flash:w:{0}:i -b {1} -carduino -pm328p -P{2}".format(fname, self.flash_baudrate, self._port))
        if status != 0:
            self._logger.error("Failed to flash firmware")
        return status == 0

    def _connect(self):
        self._logger.debug("Trying to connect Arduino on port: {0}".format(self._port))
        # open serial port
        try:
            self._serial = serial.Serial(str(self._port), int(self._baudrate), timeout=3)
            time.sleep(1)
        except:
            self._logger.error("Could not open serial port")

    def _close(self):
        self._serial.close()

    def _openSerial(self):
        basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
        flash_file_version = max(sorted(glob.iglob(basedir+'/firmware/'+str(self.config.file.connector.firmware)+'_*.hex'),  key=os.path.getctime, reverse=True))

        flash_version_number = os.path.basename(os.path.normpath(os.path.splitext(flash_file_version.split('_', 1)[-1])[0]))

        self._logger.debug("Latest available firmware version is: {0}".format(flash_version_number))

        try:
           # check if device is available
           if self.avr_device_is_available():
                   time.sleep(0.5)
                   # try to connect to arduino
                   self._connect()

                   # if connection is opened successfully
                   if self._serial.isOpen():
                           current_version = self.checkVersion()
                           self._logger.debug("Installed firmware version: {0}".format(current_version))
                           # check if autoflash is active
                           if self.config.file.connector.autoflash == "True":
                               ## check if firmware is up to date, if not flash new firmware
                               if not current_version == flash_version_number:
                                   self._close()
                                   self._logger.info("Old or no firmare detected trying to flash current firmware...")
                                   if self.avr_flash(flash_file_version):
                                        time.sleep(0.5)
                                        self._connect()
                                        current_version = self.checkVersion()
                                        self._logger.info("Successfully flashed new Firmware Version: {0}".format(current_version))


                   # no firmware is installed, flash firmware
                   else:
                            # if auto flash is activated
                            if self.config.file.connector.autoflash == "True":
                                    self._logger.info("No firmware detected trying to flash firmware...")
                                    if self.avr_flash(flash_file_version):
                                        time.sleep(0.5)
                                        self._connect()
                                        current_version = self.checkVersion()
                                        self._logger.info("Successfully flashed Firmware Version: {0}".format(current_version))
           else:
                    self._logger.error("Communication error on port {0} try other flashing baudrate than {1}. Maybe corrupted bootloader.".format(self._port, self.flash_baudrate))


           # set connection states and version
           if self._serial.isOpen() and (current_version != "None"):
                  self._logger.info("FabScanPi is connected to FabScanPi HAT or compatible on port: {0}".format(self._port))
                  current_version = self.checkVersion()
                  self._firmware_version = current_version
                  self._connected = True
           else:
                  self._logger.error("Can not find Arduino or FabScanPi HAT")
                  self._connected = False
                  sys.exit(1)

        except Exception as e:
            self._logger.error("Fatal FabScanPi HAT or compatible connection error: {0}".format(e))
            sys.exit(1)

    def checkVersion(self):
        if self._serial:
            try:
                self._serial.write("\r\n\r\n".encode())
                time.sleep(2) # Wait for FabScan to initialize
                self._serial.flushInput() # Flush startup text in serial input
                self.send("M200;")
                #command = self.send_and_receive("M200;")

                self._serial.readline()
                # receive version number
                value = self._serial.readline()
                value = value.strip()
                if value != "":
                    return value.decode()
                else:
                    return "None"
            except Exception as e:
                self._logger.error("Check Version Error: {0}".format(e))
        else:
            return "None"

    def send_and_receive(self, message):
        self.send(message)
        self._serial.flush()
        while True:
            try:
                command = self.readline()
                command = self.readline()
                return command.decode()
            except Exception as e:
                self._logger.debug("Send/Receive Error: {0}".format(e))
                break


    def readline(self):
        read_timeout = False
        try:
            i = self.buf.find(b"\n")
            if i >= 0:
                r = self.buf[:i+1]
                self.buf = self.buf[i+1:]
                return r
            while not read_timeout:
                i = max(1, min(2048, self._serial.in_waiting))
                data = self._serial.read(i)

                if not data:
                    read_timeout = True
                    self._serial.flushInput()
                    self._serial.flushOutput()
                    self._logger.debug("Serial read timeout occured, skipping current and waiting for next command.")

                i = data.find(b"\n")
                if i >= 0:
                    r = self.buf + data[:i+1]
                    self.buf[0:] = data[i+1:]
                    return r
                else:
                    self.buf.extend(data)
        except Exception as err:
            self._logger.error("Serial Error occured: {0}".format(err))


    def flush(self):
       self._serial.flushInput()
       self._serial.flushOutput()

    def send(self, message):
        try:
            message = message + "\n"
            self._serial.write(message.encode())
        except Exception as e:
            self._logger.error("Error while sending: {0}".format(e))

    def is_connected(self):
        return self._connected

    def get_firmware_version(self):
        return self._firmware_version

    def move_turntable(self, steps, speed, blocking=True):

        gcode = "01"

        if bool(blocking) is True:
            gcode = "02"

        command = "G{0} T{1} F{2}".format(gcode, steps, speed)
        #self._logger.debug(command)
        self.send_and_receive(command)

    def laser_on(self, laser):
        if laser == 0:
            command = "M21"
        else:
            command = "M19"
        #self._logger.debug("Laser {0} Switched on".format(laser))
        self.send_and_receive(command)

    def laser_off(self, laser):
        if laser == 0:
            command = "M22"
        else:
            command = "M20"
        #self._logger.debug("Laser {0} Switched off".format(laser))
        self.send_and_receive(command)

    def light_on(self, red, green, blue):
        command = "M05 R{0} G{1} B{2}".format(red, green, blue)
        self.send_and_receive(command)

    def light_off(self):
        command = "M05 R0 G0 B0"
        self.send_and_receive(command)
