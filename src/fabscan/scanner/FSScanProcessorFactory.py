from fabscan.scanner.FSLaserScanProcessor import FSLaserScanProcessor

class FSScanProcessorFactory(object):
    __scanner_classes = {
        "laser": FSLaserScanProcessor
    }

    @staticmethod
    def get_scanner_obj(name, *args, **kwargs):
       scanner_class = FSScanProcessorFactory.__scanner_classes.get(name.lower(), None)

       if scanner_class:
           return scanner_class(*args, **kwargs)
       raise NotImplementedError("The requested Scanner has not been implemented")