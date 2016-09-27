import importlib

class FSScannerFactory(object):

    @staticmethod
    def injectScannerType(type):
        try:
            scanner_type = importlib.import_module('fabscan.scanner.'+str(type))
            scanner_type.create()
        except:
            pass
