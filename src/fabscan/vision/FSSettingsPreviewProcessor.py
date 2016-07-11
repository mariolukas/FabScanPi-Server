__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import pykka
from fabscan.hardware.FSHardwareControllerFactory import FSHardwareControllerFactory
from fabscan.FSEvents import FSEvents, FSEventManager
from fabscan.vision.FSImageProcessorFactory import FSImageProcessorFactory
from fabscan.FSConfig import Config
from fabscan.FSSettings import Settings


class FSSettingsPreviewProcessor(pykka.ThreadingActor):

    def __init__(self):
        super(FSSettingsPreviewProcessor, self).__init__()
        self.eventManager = FSEventManager.instance()
        self.config = Config.instance()
        self.settings = Settings.instance()
        self.hardwareController = FSHardwareControllerFactory.get_hardware_controller_instance(self.config.scanner_type)
        self._image_processor = FSImageProcessorFactory.get_image_processor_class(self.config.scanner_type)

    def on_receive(self, event):

        if event['type'] == "CALIBRATION_IMAGE_STREAM":
            return self.create_calibration_stream()

        if event['type'] == "DEPTH_IMAGE_STREAM":
            return self.create_depth_stream()

        if event['type'] == "TEXTURE_IMAGE_STREAM":
            return self.create_texture_stream()

    def create_texture_stream(self):
        image = self.hardwareController.camera.getFrame()
        #image = self._image_processor.get_texture_stream_frame(image)
        return image

    def create_calibration_stream(self):
        image = self.hardwareController.camera.getFrame()
        image = self._image_processor.get_calibration_stream_frame(image)
        return image

    def create_depth_stream(self):
        try:
            image = self.hardwareController.camera.getFrame()
            image = self._image_processor.get_laser_stream_frame(image)
            return image
        except:
            ## catch image process error, e.g. when mjpeg stream is interupted
            pass
