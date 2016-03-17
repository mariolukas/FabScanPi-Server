__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from FSLaser import Laser
from FSTurntable import Turntable
from FSLed import Led
import time

from fabscan.controller.FSCamera import FSCamera
from fabscan.controller.FSSerial import FSSerialCom


from fabscan.FSConfig import Config
from fabscan.FSSettings import Settings
from fabscan.vision.FSImageProcessor import ImageProcessor
from fabscan.util.FSSingleton import SingletonMixin


class HardwareController(SingletonMixin):
    """
    Wrapper class for getting the Laser, Camera, and Turntable classes working
    together
    """
    def __init__(self):
        self.config = Config.instance()
        self.settings = Settings.instance()

        self.camera = None
        self._image_processor = ImageProcessor(self.config, self.settings)
        self.camera = FSCamera()
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

        #while (last_angle != current_angle):
       #     last_angle = current_angle
        #    current_angle = self.get_laser_angle()

        #angle_delta = 1
        #while(not (angle_delta < 0.3 and angle_delta > -0.3)):
        #    laser_angle = self.get_laser_angle()
        #    angle_delta = 30 - laser_angle

         #   if angle_delta > 0.3:
         #       self.laser.turn(1)
         #   elif angle_delta < -0.3:
         #       self.laser.turn(-1)

        #delta_angle = 30 - first_detected_angle
        #steps = delta_angle/0.1125*3200
        #self.laser.turn(int(360/steps))

        #angle = self.get_laser_angle()

        self.laser.off()
        return current_angle


