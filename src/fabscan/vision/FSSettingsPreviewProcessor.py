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

        if event['type'] == 'THRESHOLD':
            return self.create_threshold_preview()

        if event['type'] == 'CAMERA_PREVIEW':
            return self.create_camera_preview()

        if event['type'] == 'TEXTURE_PREVIEW':
            return self.create_texture_preview()

    def create_threshold_preview(self):
        return None

    def create_texture_preview(self):
        image = self.hardwareController.get_picture()
        image = self._image_processor.get_texture_preview_image(image)

        return image

    def create_camera_preview(self):
        try:
            image = self.hardwareController.get_picture()
            image = self._image_processor.get_preview_image(image)
            return image
        except:
            ## catch image process error, e.g. when mjpeg stream is interupted
            pass
