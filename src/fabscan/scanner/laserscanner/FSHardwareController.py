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
import cv2

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

        self._logger.debug("Reset FabScanPi HAT...")
        self.laser.off()
        self.led.off()
        self.turntable.stop_turning()
        self._logger.debug("Hardware controller initialized...")


    def settings_mode_on(self):
        self.laser.on()
        self.turntable.start_turning()
        self.camera.device.startStream()


    def settings_mode_off(self):
        self.turntable.stop_turning()
        self.led.off()
        self.laser.off()

    def get_picture(self):
        img = self.camera.device.getFrame()
        return img

    def get_pattern_image(self):
        self.led.on(110, 110, 110)
        #self.camera.device.contrast = 40
        pattern_image = self.get_picture()
        self.led.off()
        return pattern_image

    def get_laser_image(self, index):
        #self._hardwarecontroller.led.on(30, 30, 30)
        self.laser.on()

        #self.camera.device.flushStream()
        time.sleep(2)
        laser_image = self.get_picture()
        self.laser.off()
        return laser_image

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

    def start_camera_stream(self):
        self.camera.device.startStream()

    def stop_camera_stream(self):
        self.camera.device.stopStream()

    def calibrate_scanner(self):
        self._logger.debug("Startup calibration sequence started.")
        #self.laser.on()
        #self.camera.device.startStream()
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