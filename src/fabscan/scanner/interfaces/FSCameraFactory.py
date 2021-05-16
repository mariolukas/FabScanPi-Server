from fabscan.scanner.laserscanner.driver.FSCameraDummy import FSCameraDummy
try:
    from fabscan.scanner.laserscanner.driver.FSCameraPi import FSCameraPi
    from fabscan.scanner.laserscanner.driver.FSCameraV4L import FSCameraV4L
except ImportError:
    from fabscan.scanner.laserscanner.driver.FSCameraDummy import FSCameraDummy as FSCameraPi

class FSCameraFactory:

    @staticmethod
    def create(camera_type):
        _cameraConnectorTypes = {
            "PICAM": FSCameraPi,
            "dummy": FSCameraDummy,
            "V4L": FSCameraV4L,
        }

        cls = _cameraConnectorTypes[camera_type]
        return cls()
