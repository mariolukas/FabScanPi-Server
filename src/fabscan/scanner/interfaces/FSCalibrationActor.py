__author__ = "Mario Lukas"
__copyright__ = "Copyright 2016"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from pykka import ThreadingActor
import logging

class FSCalibrationActorInterface(ThreadingActor):
    def __init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller):
        pass