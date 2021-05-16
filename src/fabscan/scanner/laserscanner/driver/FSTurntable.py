__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from fabscan.lib.util.FSInject import inject
from fabscan.FSConfig import ConfigInterface

@inject(
    config=ConfigInterface
)
class Turntable(object):
    def __init__(self, hardware_connector, config):
        self.config = config
        self.hardware_connector = hardware_connector
        # Number of steps for the turntable to do a full rotation
        # DEFAULT Value for FS Shield is 1/16 Step
        self.steps_for_full_rotation = self.config.file.turntable.steps
        # scaler for silent step sticks was in firmware before.
        self.scaler = 4

    def step(self, steps, speed):
        '''
        Accepts number of steps to take
        '''
        steps *= self.scaler
        if self.hardware_connector:
            self.hardware_connector.move_turntable(steps, speed, blocking=False)

    def step_blocking(self, steps, speed):
        steps *= self.scaler
        if self.hardware_connector:
            self.hardware_connector.move_turntable(steps, speed, blocking=True)

    def enable_motors(self):
        if self.hardware_connector:
            command = "M17"
            self.hardware_connector.send_and_receive(command)

    def disable_motors(self):
        if self.hardware_connector:
            command = "M18"
            self.hardware_connector.send_and_receive(command)

    def start_turning(self):
        if self.hardware_connector:
            self.enable_motors()
            command = "G06"
            self.hardware_connector.send_and_receive(command)

    def stop_turning(self):
        if self.hardware_connector:
            self.disable_motors()
            command = "G07"
            self.hardware_connector.send_and_receive(command)

