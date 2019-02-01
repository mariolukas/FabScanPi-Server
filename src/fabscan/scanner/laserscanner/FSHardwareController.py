__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import logging
import time
import threading

from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.lib.util.FSInject import singleton
from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface

from fabscan.scanner.laserscanner.driver.FSTurntable import Turntable
from fabscan.scanner.laserscanner.driver.FSCamera import FSCamera
from fabscan.scanner.laserscanner.driver.FSSerial import FSSerialCom
from fabscan.scanner.laserscanner.driver.FSLaser import Laser
from fabscan.scanner.laserscanner.driver.FSLed import Led

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
        self.lock = threading.Lock()

    def flush(self):
        self.camera.camera_buffer.flush()
        #self.serial_connection.flush()

        self.hardware_test_functions = {
            "TURNTABLE": {
                "FUNCTIONS": {
                    "START": self.turntable.start_turning,
                    "STOP": self.turntable.stop_turning
                },
                "LABEL": "Turntable"
            },
            "LEFT_LASER": {
                "FUNCTIONS": {
                    "ON": lambda: self.laser.on(0),
                    "OFF": lambda: self.laser.off(0)
                },
                "LABEL": "First Laser"
            },
            "RIGHT_LASER": {
                "FUNCTIONS": {
                    "ON": lambda: self.laser.on(1),
                    "OFF": lambda: self.laser.off(1)
                },
                "LABEL": "Second Laser"
            },
            "LED_RING": {
                "FUNCTIONS": {
                    "ON": lambda: self.led.on(255, 255, 255),
                    "OFF": lambda: self.led.off()
                },
                "LABEL": "Led Ring"
            }
        }


    def get_devices_as_json(self):
        devices = copy.deepcopy(self.hardware_test_functions)
        for fnct in self.hardware_test_functions:
            devices[fnct]['FUNCTIONS'] = self.hardware_test_functions[fnct]['FUNCTIONS'].keys()
        return devices


    def call_test_function(self, device):
        device_name = str(device.name)
        device_value = str(device.function)
        #self._logger.debug(device)
        call_function = self.hardware_test_functions.get(device_name).get("FUNCTIONS").get(device_value)
        call_function()

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
        time.sleep(0.3)


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

        self.turntable.step(steps, speed=900)
        time.sleep(0.7)
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