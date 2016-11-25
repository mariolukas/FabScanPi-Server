
import logging


from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.FSEvents import FSEventManagerSingleton, FSEvents, FSEvent
from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.scanner.interfaces.FSCalibration import FSCalibrationInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface

@singleton(
    config=ConfigInterface,
    settings=SettingsInterface,
    eventmanager=FSEventManagerSingleton,
    imageprocessor=ImageProcessorInterface,
    hardwarecontroller=FSHardwareControllerInterface
)
class FSCalibrationSingleton(FSCalibrationInterface):
    def __init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller):
        super(FSCalibrationInterface, self).__init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller)
