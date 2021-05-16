__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import logging
import time
import cv2

from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.lib.util.FSInject import singleton
from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface
from fabscan.lib.file.FSImage import FSImage

from fabscan.scanner.laserscanner.driver.FSTurntable import Turntable
from fabscan.scanner.laserscanner.driver.FSLaser import Laser
from fabscan.scanner.laserscanner.driver.FSLed import Led
from fabscan.scanner.interfaces.FSHardwareConnectorFactory import FSHardwareConnectorFactory
from fabscan.scanner.interfaces.FSCameraFactory import FSCameraFactory
from memory_profiler import profile

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
        # debug
        self.image = FSImage()

        self._logger = logging.getLogger(__name__)
        self._settings_mode_is_off = True
        self.camera = None
        self._image_processor = imageprocessor
        self.hardware_connector = FSHardwareConnectorFactory.create(self.config.file.connector.type)
        self.turntable = Turntable(hardware_connector=self.hardware_connector)
        self.laser = Laser(self.hardware_connector)
        self.led = Led(self.hardware_connector)

        self.led.on(255, 255, 255)
        time.sleep(0.5)
        self.camera = FSCameraFactory.create(self.config.file.camera.type).start_stream()
        self.led.off()

        self._logger.debug("Reset FabScanPi HAT...")
        self.reset_devices()

        self._logger.debug("Hardware controller initialized...")

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

    def reset_devices(self):
        for laser_index in range(self.config.file.laser.numbers):
            self.laser.off(laser_index)
        self.led.off()
        self.turntable.stop_turning()

    def flush(self):
        pass

    def get_devices_as_json(self):

        devices = dict()
        for device in self.hardware_test_functions:
            devices[device] = dict()
            devices[device]['FUNCTIONS'] = list(self.hardware_test_functions[device]['FUNCTIONS'].keys())
            devices[device]['LABEL'] = self.hardware_test_functions[device]['LABEL']

        return devices

    def call_test_function(self, device):
        device_name = str(device.name)
        device_value = str(device.function)
        call_function = self.hardware_test_functions.get(device_name).get("FUNCTIONS").get(device_value)
        call_function()


    def settings_mode_on(self):
        self._settings_mode_is_off = False
        self.laser.on(laser=0)

    def settings_mode_off(self):
        self.reset_hardware()
        self._settings_mode_is_off = True

    def get_picture(self, flush=False, preview=False):
        if not self.camera:
            self.camera = FSCameraFactory.create(self.config.file.camera.type).start_stream()
        try:
            img = self.camera.get_frame(preview=preview)
        except Exception as e:
            self._logger.error("Error while get_picture: {0}".format(e))
        return img

    def get_pattern_image(self):

            self.led.on(110, 110, 110)
            #self.camera.contrast = 40
            pattern_image = self.get_picture()
            self.led.off()
            return pattern_image

    def reset_hardware(self):
        self.led.off()

        for i in range(self.config.file.laser.numbers):
            self.laser.off(i)

        self.turntable.stop_turning()
        self.turntable.disable_motors()


    def get_laser_image(self, index):
            self.laser.on(laser=index)
            time.sleep(0.4)
            laser_image = self.get_picture(flush=True)
            self.laser.off(laser=index)
            return laser_image

    def get_camera(self):
        return self.camera


    def get_image_at_position(self, index=0):
        '''
        Take a step and return an image.
        Step size calculated to correspond to num_steps_per_rotation
        Returns resulting image
        '''

        laser_image = self.get_laser_image(index)

        if self.config.file.laser.interleaved == "True":
            backrgound_image = self.get_picture(flush=True)
            laser_image = cv2.absdiff(backrgound_image, laser_image)
            del backrgound_image
        return laser_image

    def move_to_next_position(self, steps=180, speed=2000, blocking=True):
        self.turntable.step_blocking(steps, speed)

    def hardware_connector_available(self):
        return self.hardware_connector.is_connected()

    def get_firmware_version(self):
        return self.hardware_connector.get_firmware_version()

    def camera_is_connected(self):
       return True
       #TODO: implement this
       #return self.camera.is_connected()

    def start_camera_stream(self):
       self.camera = FSCameraFactory.create(self.config.file.camera.type).start_stream()

    def stop_camera_stream(self):
       self.camera.stop_stream()
       self.camera = None

