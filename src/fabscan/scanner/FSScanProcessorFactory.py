__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from fabscan.scanner.FSLaserScanProcessor import FSLaserScanProcessor

class FSScanProcessorFactory():
    __scanner_classes = {
        "laser": FSLaserScanProcessor
    }

    @staticmethod
    def get_scanner_obj(name, *args, **kwargs):
       scanner_class = FSScanProcessorFactory.__scanner_classes.get(name.lower())

       if scanner_class:
           return scanner_class.start()
       raise NotImplementedError("The requested Scanner has not been implemented")