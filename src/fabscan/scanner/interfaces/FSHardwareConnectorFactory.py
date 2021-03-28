from fabscan.scanner.laserscanner.driver.FSSerial import FSSerialCom
from fabscan.scanner.laserscanner.driver.FSSerialDummy import FSSerialDummy

class FSHardwareConnectorFactory:

    @staticmethod
    def create(connector_type):
        _hardwareConnectorTypes = {
            "serial": FSSerialCom,
            "dummy": FSSerialDummy,
        }

        cls = _hardwareConnectorTypes[connector_type]
        return cls()
