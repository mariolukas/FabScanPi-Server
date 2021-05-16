__copyright__ = "Copyright 2020"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import cv2
import logging
import numpy as np
import threading, collections
from fabscan.lib.util.FSInject import inject, singleton
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
import queue as Queue


@inject(
    config=ConfigInterface,
    settings=SettingsInterface
)
class Video4LStream:

    def __init__(self, name, config, settings):
        self.config = config
        self.settings = settings
        self._logger = logging.getLogger(__name__)
        self.cap = cv2.VideoCapture(name)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1232)
        self.high_res_q = Queue.Queue()
        self.low_res_q = Queue.Queue()


    def start_stream(self):
        self._logger.debug("Starting")
        t = threading.Thread(target=self.update, name=__name__+'-Thread', args=())
        t.daemon = True
        t.start()
        return self

    # read frames as soon as they are available, keeping only most recent one
    def update(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                global is_frame
                is_frame = False
                break
            if not self.high_res_q.empty():
                try:
                    self.high_res_q.get_nowait()   # discard previous (unprocessed) frame
                    self.low_res_q.get_nowait()
                except Queue.Empty:
                    pass
            self.create_low_res_image(frame)
            self.high_res_q.put(frame)


    def create_low_res_image(self, image):
        low_res_size = (self.config.file.camera.preview_resolution.width, self.config.file.camera.preview_resolution.height)
        image = cv2.resize(image, low_res_size)
        self.low_res_q.put(image)
        return image

    def get_frame(self, preview):
        if preview:
            return self.low_res_q.get()
        else:
            return self.high_res_q.get()

@singleton(
    config=ConfigInterface,
    settings=SettingsInterface
)
class FSCameraV4L(threading.Thread):

    def __init__(self, config, settings):

        self._logger = logging.getLogger(__name__)
        self.config = config
        self.settings = settings
        self.stream = Video4LStream(0, config=self.config, settings=self.settings)

    def get_frame(self, preview=False):
        return self.stream.get_frame(preview=preview)

    def start_stream(self):
        self._logger.debug("Called")
        return self.stream.start_stream()

    def stop_stream(self):
        self.stream.stop_stream()

    def is_idle(self):
        pass

    def flush_stream(self):
        pass