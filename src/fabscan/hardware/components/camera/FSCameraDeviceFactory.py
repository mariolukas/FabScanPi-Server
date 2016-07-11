__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from fabscan.hardware.components.camera.FSC270 import C270
from fabscan.hardware.components.camera.FSDummyCam import DummyCam
from fabscan.hardware.components.camera.FSPiCam import PiCam

class FSCameraDeviceFactory():
    __camera_classes = {
        "picam": PiCam,
        "c270": C270,
        "dummy": DummyCam
    }

    @staticmethod
    def get_camera_device_obj(name, *args, **kwargs):
       camera_device_class = FSCameraDeviceFactory.__camera_classes.get(name.lower())()

       if camera_device_class:
           return camera_device_class

       raise NotImplementedError("The requested HardwareController has not been implemented")