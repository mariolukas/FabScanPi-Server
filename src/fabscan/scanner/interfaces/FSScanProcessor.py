__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from pykka import ThreadingActor


class FSScanProcessorCommand(object):
    START = "START"
    STOP = "STOP"
    STOP_CALIBRATION = "STOP_CALIBRATION"
    START_CALIBRATION = "START_CALIBRATION"
    SETTINGS_MODE_OFF = "SETTINGS_MODE_OFF"
    SETTINGS_MODE_ON = "SETTINGS_MODE_ON"
    NOTIFY_HARDWARE_STATE = "NOTIFY_HARDWARE_STATE"
    UPDATE_SETTINGS = "UPDATE_SETTINGS"
    UPDATE_CONFIG = "UPDATE_CONFIG"
    _SCAN_NEXT_TEXTURE_POSITION = "SCAN_NEXT_TEXTURE_POSITION"
    _SCAN_NEXT_OBJECT_POSITION = "SCAN_NEXT_OBJECT_POSITION"
    GET_HARDWARE_INFO = "GET_HARDWARE_INFO"
    GET_CALIBRATION_STREAM = "GET_CALIBRATION_STREAM"
    GET_LASER_STREAM = "GET_LASER_STREAM"
    GET_ADJUSTMENT_STREAM = "GET_ADJUSTMENT_STREAM"
    GET_TEXTURE_STREAM = "GET_TEXTURE_STREAM"
    GET_SETTINGS_STREAM = "GET_SETTINGS_STREAM"
    NOTIFY_IF_NOT_CALIBRATED = "NOTIFY_IF_NOT_CALIBRATED"
    CALL_HARDWARE_TEST_FUNCTION = "CALL_HARDWARE_TEST_FUNCTION"
    CONFIG_MODE_ON = "CONFIG_MODE_ON"
    CONFIG_MODE_OFF = "CONFIG_MODE_OFF"
    IMAGE_PROCESSED = "IMAGE_PROCESSED"


class FSScanProcessorInterface(ThreadingActor):
    def __init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller, calibration, workerpool):
        super(FSScanProcessorInterface, self).__init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller, calibration, workerpool)
        pass
