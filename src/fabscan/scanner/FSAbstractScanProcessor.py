__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import abc
import pykka
from fabscan.FSEvents import FSEvents

class FSScanProcessorCommand(object):
    START = "START"
    STOP = "STOP"
    SETTINGS_MODE_OFF = "SETTINGS_MODE_OFF"
    SETTINGS_MODE_ON = "SETTINGS_MODE_ON"
    NOTIFY_HARDWARE_STATE = "NOTIFY_HARDWARE_STATE"
    UPDATE_SETTINGS = "UPDATE_SETTINGS"
    SCAN_NEXT_TEXTURE_POSITION = "SCAN_NEXT_TEXTURE_POSITION"
    SCAN_NEXT_OBJECT_POSITION = "SCAN_NEXT_OBJECT_POSITION"

class FSAbstractScanProcessor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        super(FSAbstractScanProcessor, self).__init__()
        pass

    @abc.abstractmethod
    def start_scan(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def stop_scan(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def settings_mode_on(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def settings_mode_off(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def scan_next_texture_position(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def scan_next_object_position(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def send_hardware_state_notification(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def update_settings(self, *args, **kwargs):
        pass