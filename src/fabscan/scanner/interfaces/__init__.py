import importlib
import logging

logger = logging.getLogger(__name__)

class FSScannerFactory(object):

    @staticmethod
    def injectScannerType(type):
        try:
            logger.debug('Scanner Type is: '+str(type))
            scanner_type = importlib.import_module('fabscan.scanner.'+str(type))
            scanner_type.create()
        except Exception as e:
            logger.exception("Error ")
            pass
