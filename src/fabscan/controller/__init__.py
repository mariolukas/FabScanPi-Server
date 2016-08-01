__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from FSLaser import Laser
from FSTurntable import Turntable
from FSLed import Led
import time
import logging

from fabscan.controller.FSCamera import FSCamera
from fabscan.controller.FSSerial import FSSerialCom


from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.vision.FSImageProcessor import ImageProcessorInterface
from fabscan.util.FSInject import singleton, inject

class FSHardwareControllerInterface(object):

    def __init__(self, config, settings, imageprocessor):
        pass

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

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        self.config = config.instance
        self.settings = settings.instance

        self.camera = None
        self._image_processor = imageprocessor
        self.camera = FSCamera()
        self.serial_connection = FSSerialCom()

        self.turntable = Turntable(self.serial_connection)

        self.laser = Laser(self.serial_connection)
        self.led = Led(self.serial_connection)

        self.laser.off()
        self.led.off()
        self.turntable.stop_turning()
        self.turntable.disable_motors()

        self._logger.debug("Hardware controller initialized...")

    def settings_mode_on(self):
        self.laser.on()
        self.turntable.start_turning()
        self.camera.device.startStream()



    def settings_mode_off(self):
        self.turntable.stop_turning()
        self.led.off()
        self.laser.off()
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

    def calibrate_laser(self):
        self.laser.on()
        time.sleep(0.8)
        last_angle = 0
        current_angle = self.get_laser_angle()
        self.laser.off()
        return current_angle