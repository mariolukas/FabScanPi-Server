from fabscan.scanner.laserscanner.driver.FSCameraDummy import FSCameraDummy
from fabscan.scanner.laserscanner.driver.FSCameraV4L import FSCameraV4L
import logging

availableConnectorTypes = {
    "dummy": FSCameraDummy,
    "V4L": FSCameraV4L,
}

try:
    from fabscan.scanner.laserscanner.driver.FSCameraPi import FSCameraPi
    availableConnectorTypes = {
        "PICAM": FSCameraPi,
        "dummy": FSCameraDummy,
        "V4L": FSCameraV4L,
    }

except ImportError:
    log = logging.getLogger(__name__)
    log.warning("Not able to load module picamera")

class FSCameraFactory:

    @staticmethod
    def create(camera_type):
        _cameraConnectorTypes = availableConnectorTypes
        cls = _cameraConnectorTypes[camera_type]
        return cls()
