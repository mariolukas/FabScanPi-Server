__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import pykka
from fabscan.controller import HardwareController
from fabscan.FSEvents import FSEvents, FSEventManager
from fabscan.vision.FSImageProcessor import ImageProcessor
from fabscan.FSConfig import Config
from fabscan.FSSettings import Settings


class FSSettingsPreviewProcessor(pykka.ThreadingActor):

    def __init__(self):
        super(FSSettingsPreviewProcessor, self).__init__()
        self.hardwareController = HardwareController.instance()
        self.eventManager = FSEventManager.instance()
        self.config = Config.instance()
        self.settings = Settings.instance()
        self._image_processor = ImageProcessor(self.config, self.settings)


    def on_receive(self, event):

        if event['type'] == "CALIBRATION_STREAM":
            return self.create_calibration_stream()

        if event['type'] == "LASER_STREAM":
            return self.create_laser_stream()

        if event['type'] == "TEXTURE_STREAM":
            return self.create_texture_stream()

    def create_threshold_preview(self):
        return None

    def create_texture_stream(self):
        image = self.hardwareController.get_picture()
        image = self._image_processor.get_texture_stream_frame(image)

        return image

    def create_calibration_stream(self):
        image = self.hardwareController.get_picture()
        image = self._image_processor.get_calibration_stream_frame(image)

        return image

    def create_laser_stream(self):
        try:
            image = self.hardwareController.get_picture()
            image = self._image_processor.get_laser_stream_frame(image)
            return image
        except:
            ## catch image process error, e.g. when mjpeg stream is interupted
            pass
