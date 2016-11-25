__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from fabscan.util.FSInject import injector
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorInterface
from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface
from fabscan.scanner.interfaces.FSCalibration import FSCalibrationInterface
from fabscan.scanner.laserscanner.FSScanProcessor import FSScanProcessorSingleton
from fabscan.scanner.laserscanner.FSHardwareController import FSHardwareControllerSingleton
from fabscan.scanner.laserscanner.FSCalibration import FSCalibrationSingleton
from fabscan.scanner.laserscanner.FSImageProcessor import ImageProcessor

def create():
    # "dynamic" module classes ...

    injector.provide(ImageProcessorInterface, ImageProcessor)
    injector.provide(FSHardwareControllerInterface, FSHardwareControllerSingleton)
    injector.provide(FSScanProcessorInterface, FSScanProcessorSingleton)
    injector.provide(FSCalibrationInterface, FSCalibrationSingleton)

