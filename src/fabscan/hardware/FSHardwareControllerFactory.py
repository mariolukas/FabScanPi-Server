__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from fabscan.hardware.FSLaserScannerHardwareController import FSLaserScannerHardwareController

class FSHardwareControllerFactory():
    __hardware_controller_classes = {
        "laser": FSLaserScannerHardwareController
    }

    @staticmethod
    def get_hardware_controller_instance(name, *args, **kwargs):
       hardware_controller_class = FSHardwareControllerFactory.__hardware_controller_classes.get(name.lower()).instance()

       if hardware_controller_class:
           return hardware_controller_class

       raise NotImplementedError("The requested HardwareController has not been implemented")