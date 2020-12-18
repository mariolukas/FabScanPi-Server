from fabscan.scanner.laserscanner.driver.FSSerial import FSSerialCom

class FSHardwareConnectorFactory:

    @staticmethod
    def create(connector_type):
        _hardwareConnectorTypes = {
            "serial": FSSerialCom,
        }

        cls = _hardwareConnectorTypes[connector_type]
        return cls()
