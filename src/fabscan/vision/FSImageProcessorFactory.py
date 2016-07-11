__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from fabscan.FSConfig import Config
from fabscan.FSSettings import Settings
from fabscan.vision.FSLaserImageProcessor import FSLaserImageProcessor

class FSImageProcessorFactory():
    __image_processor_classes = {
        "laser": FSLaserImageProcessor
    }

    @staticmethod
    def get_image_processor_class(name, *args, **kwargs):
       image_processor_class = FSImageProcessorFactory.__image_processor_classes.get(name.lower())(Config.instance(), Settings.instance())

       if image_processor_class:
           return image_processor_class

       raise NotImplementedError("The requested ImageProcessor has not been implemented")