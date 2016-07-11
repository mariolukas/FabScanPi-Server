__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time

from fabscan.FSConfig import Config
from fabscan.FSSettings import Settings
from fabscan.hardware.FSAbstractHadrwareController import FSAbstractHadrwareController
from fabscan.vision.FSImageProcessorFactory import FSImageProcessorFactory
from fabscan.hardware.components.FSSerial import FSSerialCom
from fabscan.hardware.components.FSLaser import Laser
from fabscan.hardware.components.FSTurntable import Turntable
from fabscan.hardware.components.FSLed import Led
from fabscan.hardware.components.camera.FSCameraDeviceFactory import FSCameraDeviceFactory



class FSLaserScannerHardwareController(FSAbstractHadrwareController):
    """
    Wrapper class for getting the Laser, Camera, and Turntable classes working
    together
    """
    def __init__(self):
        super(FSLaserScannerHardwareController, self).__init__()
        self.config = Config.instance()
        self.settings = Settings.instance()
        self._image_processor = FSImageProcessorFactory.get_image_processor_class(self.config.scanner_type)
        self.camera = FSCameraDeviceFactory.get_camera_device_obj(self.config.camera.type)
        self.serial_connection = FSSerialCom()
        self.turntable = Turntable(self.serial_connection)
        self.laser = Laser(self.serial_connection)
        self.led = Led(self.serial_connection)
        self.laser.off()
        self.led.off()
        self.turntable.stop_turning()
        self.turntable.disable_motors()

    def settings_mode_on(self):
        self.laser.on()
        self.turntable.start_turning()
        self.camera.startStream()

    def settings_mode_off(self):
        self.turntable.stop_turning()
        self.led.off()
        self.laser.off()
        self.camera.flushStream()
        self.camera.stopStream()

    def get_picture(self):
        img = self.camera.getFrame()
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
        img = self.camera.getFrame()
        return img

    def get_laser_angle(self):
        image = self.camera.getFrame()
        angle = self._image_processor.calculate_laser_angle(image)
        return angle

    def arduino_is_connected(self):
        return self.serial_connection.is_connected()

    def get_firmware_version(self):
        return self.serial_connection.get_firmware_version()

    def camera_is_connected(self):
       return self.camera.isAlive()

    def calibrate_laser(self):
        self.laser.on()
        time.sleep(0.8)
        last_angle = 0
        current_angle = self.get_laser_angle()
        self.laser.off()
        return current_angle