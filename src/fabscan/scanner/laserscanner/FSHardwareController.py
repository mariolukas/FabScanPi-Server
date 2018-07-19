__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
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
        self._settings_mode_is_off = True
        self.camera = None
        self._image_processor = imageprocessor
        self.camera = FSCamera()
        self.serial_connection = FSSerialCom()

        self.turntable = Turntable(serial_object=self.serial_connection)
        self.laser = Laser(self.serial_connection)
        self.led = Led(self.serial_connection)

        self._logger.debug("Reset FabScanPi HAT...")
        self.laser.off(laser=0)
        #self.laser.off(laser=1)
        self.led.off()
        self.turntable.stop_turning()
        self._logger.debug("Hardware controller initialized...")

    def flush(self):
        self.camera.camera_buffer.flush()
        #self.serial_connection.flush()

    def settings_mode_on(self):
        while not self.camera.device.is_idle():
            time.sleep(0.1)
        self.camera.device.start_stream(mode="settings")
        self._settings_mode_is_off = False
        self.camera.device.flush_stream()
        self.laser.on(laser=0)
        self.turntable.start_turning()

    def settings_mode_off(self):
        self.turntable.stop_turning()
        self.led.off()
        self.laser.off(laser=0)
        self.camera.device.stop_stream()
        self.camera.device.flush_stream()
        self._settings_mode_is_off = True

    def get_picture(self):
        img = self.camera.device.get_frame()
        return img

    def get_pattern_image(self):
        self.led.on(110, 110, 110)
        #self.camera.device.contrast = 40
        pattern_image = self.get_picture()
        self.led.off()
        return pattern_image

    def get_laser_image(self, index):
        #self._hardwarecontroller.led.on(30, 30, 30)
        self.laser.on(laser=index)
        time.sleep(3)
        self.camera.device.flush_stream()
        laser_image = self.get_picture()
        self.laser.off(laser=index)
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
        img = self.camera.device.get_frame()
        return img


    def arduino_is_connected(self):
        return self.serial_connection.is_connected()

    def get_firmware_version(self):
        return self.serial_connection.get_firmware_version()

    def camera_is_connected(self):
       return self.camera.is_connected()

    def start_camera_stream(self, mode="default"):
        self.camera.device.start_stream(mode)

    def stop_camera_stream(self):
        self.camera.device.stop_stream()