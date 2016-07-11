__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"
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
    GET_HARDWARE_INFO = "GET_HARDWARE_INFO"

class FSAbstractScanProcessor(pykka.ThreadingActor):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        super(FSAbstractScanProcessor, self).__init__()
        pass

    def on_receive(self, event):
        # call with tell
        if event[FSEvents.COMMAND] == FSScanProcessorCommand.START:
            self.start_scan()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.STOP:
            self.stop_scan()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.SETTINGS_MODE_ON:
            self.settings_mode_on()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.SETTINGS_MODE_OFF:
            self.settings_mode_off()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.SCAN_NEXT_TEXTURE_POSITION:
            self.scan_next_texture_position()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.SCAN_NEXT_OBJECT_POSITION:
            self.scan_next_object_position()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.NOTIFY_HARDWARE_STATE:
            self.send_hardware_state_notification()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.UPDATE_SETTINGS:
            self.update_settings(event['SETTINGS'])

        # call with ask
        if event[FSEvents.COMMAND] == FSScanProcessorCommand.GET_HARDWARE_INFO:
            return self.get_hardware_info()



    @abc.abstractmethod
    def get_hardware_info(self):
        pass

    @abc.abstractmethod
    def start_scan(self):
        pass

    @abc.abstractmethod
    def stop_scan(self):
        pass

    @abc.abstractmethod
    def settings_mode_on(self):
        pass

    @abc.abstractmethod
    def settings_mode_off(self):
        pass

    @abc.abstractmethod
    def scan_next_texture_position(self):
        pass

    @abc.abstractmethod
    def scan_next_object_position(self):
        pass

    @abc.abstractmethod
    def send_hardware_state_notification(self):
        pass

    @abc.abstractmethod
    def update_settings(self):
        pass
