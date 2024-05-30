__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import cv2
import logging
import threading
from picamera2 import Picamera2
from fabscan.lib.util.FSInject import inject, singleton
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface

class PiVideoStream:
    def __init__(self, config, settings, framerate, **kwargs):
        self._logger = logging.getLogger(__name__)
        # initialize the camera
        try:
            self.camera = Picamera2()
            self.camera.start()
        except Exception as e:
            self._logger.exception(e)

        self.settings = settings

        self.high_res_frame = None
        self.low_res_frame = None
        self.stopped = False

    def start_stream(self):
        # start the thread to read frames from the video stream
        t = threading.Thread(target=self.update, name=__name__+'-Thread', args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped

        while True:

            self.low_res_frame = self.camera.capture_array("main")

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.camera.close()
                break

    def get_frame(self, preview=False):
        if preview:
            return self.low_res_frame
        else:
            return self.high_res_frame

    def stop_stream(self):
        # indicate that the thread should be stopped
        self.stopped = True

@singleton(
    config=ConfigInterface,
    settings=SettingsInterface
)
class FSCameraPi:

    def __init__(self, config, settings):

        self._logger = logging.getLogger(__name__)
        self.config = config
        self.settings = settings
        self.stream = PiVideoStream(config=self.config, settings=self.settings, framerate=32)

    def get_frame(self, preview=False):
        return self.stream.get_frame(preview=preview)

    def start_stream(self):
        return self.stream.start_stream()

    def stop_stream(self):
        self.stream.stop_stream()
        return

    def is_idle(self):
        pass

    def flush_stream(self):
        pass
