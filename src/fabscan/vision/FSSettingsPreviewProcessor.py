__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import pykka
from fabscan.controller import FSHardwareControllerSingleton
from fabscan.FSEvents import FSEvents, FSEventManager
from fabscan.vision.FSImageProcessor import ImageProcessor
from fabscan.FSConfig import Config
from fabscan.FSSettings import Settings
from fabscan.util.FSInject import inject
import logging

@inject(
        config=Config,
        settings=Settings,
        eventmanager=FSEventManager,
        hardwarecontroller=FSHardwareControllerSingleton
)
class FSSettingsPreviewProcessor(pykka.ThreadingActor):

    def __init__(self, config, settings, eventmanager, hardwarecontroller):
        super(FSSettingsPreviewProcessor, self).__init__()

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.hardwareController = hardwarecontroller
        self.eventManager = eventmanager
        self.config = config
        self.settings = settings
        self._image_processor = ImageProcessor()


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
