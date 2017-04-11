__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

STEPS_PER_ROTATION = 3200
from fabscan.util.FSInject import inject
from fabscan.FSConfig import ConfigInterface

@inject(
    config=ConfigInterface
)
class Turntable(object):
    def __init__(self, serial_object, config):
        self.config=config
        self.serial_connection = serial_object
        # Number of steps for the turntable to do a full rotation
        # DEFAULT Value for FS Shield is 1/16 Step
        self.steps_for_full_rotation = self.config.turntable.steps


    def async_step(self, steps=1):
        '''
        Accepts number of steps to take. Does not wait for it to finish turning
        '''
        if self.serial_connection != None:
            self.serial_connection.send("G04 T"+str(steps)+" F100;\n")
            self.serial_connection.wait_until_ready()

    def step(self, steps, speed):
        '''
        Accepts number of steps to take
        '''
        if self.serial_connection != None:
            self.serial_connection.send("G04 T"+str(steps)+" F"+str(speed)+";\n")
            self.serial_connection.wait_until_ready()

    def step_blocking(self, steps, speed):
        if self.serial_connection != None:
            self.serial_connection.send("G02 T"+str(steps)+" F"+str(speed)+";\n")
            self.serial_connection.wait_until_ready()

    def step_interval(self, steps, speed):
        '''
        Takes number of steps for one interval based on number of intervals in
            a rotation.
        36 would mean there are 36 turns in a rotation.
        '''
        if self.serial_connection != None:
            #steps = get_step_interval(rotation_intervals)
            self.step(steps, speed)

    def enable_motors(self):
        if self.serial_connection != None:
            self.serial_connection.send("M17;\n")
            self.serial_connection.wait_until_ready()
      #      self.serial_connection.wait()

    def disable_motors(self):
        if self.serial_connection != None:
            self.serial_connection.send("M18;\n")
            self.serial_connection.wait_until_ready()
#            self.serial_connection.wait()


    def start_turning(self):
        if self.serial_connection != None:
            self.enable_motors()
            self.serial_connection.send("G06;\n")
            self.serial_connection.wait_until_ready()

    def stop_turning(self):
        if self.serial_connection != None:
            self.disable_motors()
            self.serial_connection.send("G07;\n")
            self.serial_connection.wait_until_ready()


def get_step_interval(rotation_intervals):
    return STEPS_PER_ROTATION / rotation_intervals
