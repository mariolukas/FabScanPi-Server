__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import logging
import time

from FSLaser import Laser
from FSLed import Led
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.util.FSInject import singleton

from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface

from fabscan.scanner.laserscanner.FSTurntable import Turntable
from fabscan.scanner.laserscanner.FSCamera import FSCamera
from fabscan.scanner.laserscanner.FSSerial import FSSerialCom

@singleton(
    config=ConfigInterface,
    settings=SettingsInterface,
    imageprocessor=ImageProcessorInterface
)
class FSHardwareControllerSingleton(FSHardwareControllerInterface):
    """
    Wrapper class for getting the Laser, Camera, and Turntable classes working
    together
    """
    def __init__(self, config, settings, imageprocessor):

        self.config = config
        self.settings = settings

        self._logger = logging.getLogger(__name__)

        self.camera = None
        self._image_processor = imageprocessor
        self.camera = FSCamera()
        self.serial_connection = FSSerialCom()

        self.turntable = Turntable(serial_object=self.serial_connection)

        self.laser = Laser(self.serial_connection)
        self.led = Led(self.serial_connection)

        self.laser.off()
        self.led.off()
        self.turntable.stop_turning()
        self.turntable.disable_motors()

        self._logger.debug("Hardware controller initialized...")
        #self.hardware_calibration()

    def settings_mode_on(self):
        self.laser.on()
        self.turntable.start_turning()
        self.camera.device.startStream()


    def settings_mode_off(self):
        self.turntable.stop_turning()
        self.led.off()
        self.laser.off()
        time.sleep(0.3)
        self.camera.device.flushStream()
        self.camera.device.stopStream()


    def get_picture(self):
        img = self.camera.device.getFrame()
        return img

    def scan_at_position(self, steps=180, color=False):
        '''
        Take a step and return an image.
        Step size calculated to correspond to num_steps_per_rotation
        Returns resulting image
            '''
        if color:
            speed = 800
        else:
            speed = 50


        self.turntable.step_interval(steps, speed)
        img = self.camera.device.getFrame()
        return img


    def get_laser_angle(self):
        image = self.camera.device.getFrame()
        angle = self._image_processor.calculate_laser_angle(image)
        return angle

    def arduino_is_connected(self):
        return self.serial_connection.is_connected()

    def get_firmware_version(self):
        return self.serial_connection.get_firmware_version()

    def camera_is_connected(self):
       return self.camera.is_connected()

    def calibrate_scanner(self):
        self._logger.debug("Startup calibration sequence started.")
        #self.laser.on()
        #self.camera.device.startStream()
        time.sleep(2)
        laser_angle = self.get_laser_angle()
        self._logger.debug(laser_angle)
        #self.camera.device.stopStream()
        #self.laser.off()
        self.settings.save()
        self._logger.debug("Calibration sequence finished.")

    def calibrate_laser(self):
        self.laser.on()
        time.sleep(0.8)
        last_angle = 0
        current_angle = self.get_laser_angle()
        self.laser.off()
        return current_angle