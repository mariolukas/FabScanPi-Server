from fabscan.scanner.laserscanner.driver.FSCameraPi import FSCameraPi
from fabscan.scanner.laserscanner.driver.FSCameraDummy import FSCameraDummy

class FSCameraFactory:

    @staticmethod
    def create(camera_type):
        _cameraConnectorTypes = {
            "PICAM": FSCameraPi,
            "dummy": FSCameraDummy,
        }

        cls = _cameraConnectorTypes[camera_type]
        return cls()
