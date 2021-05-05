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
class VideoCaptureQ:

    def __init__(self, name, config, settings):
        self.config = config
        self.settings = settings
        self._logger = logging.getLogger(__name__)
        self.cap = cv2.VideoCapture(name)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.config.file.camera.resolution.width))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.config.file.camera.resolution.height))
        self.high_res_q = Queue.Queue()
        self.low_res_q = Queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
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

    def read(self, preview):
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
        self.device = VideoCaptureQ(0)
#        self.stream = cv2.VideoCapture(0)
#        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.file.camera.resolution.width)
#        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.file.camera.resolution.height)
        #self.stream.set(cv2.CV_CAP_PROP_FPS, 15)
#        (self.grabbed, self.frame) = self.stream.read()

 #       self.q = Queue.Queue()


        self.idle = True

    # def update(self, stop_event):
    #     t = threading.currentThread()
    #     # keep looping infinitely until the thread is stopped
    #     self._logger.debug("Stream started..")
    #     while stop_event.isSet():
    #         (self.grabbed, self.frame) = self.stream.read()
    #     self._logger.debug("Stream Stopped.")
    #     stop_event.clear()

    # read frames as soon as they are available, keeping only most recent one

    def get_frame(self, preview=False):
        # return the frame most recently read
        return self.device.read(False)

    def start_stream(self, mode="default"):
        self.idle = False
        # self._stop_event.set()
        # # start the thread to read frames from the video stream
        # t = threading.Thread(target=self._reader)
        # t.daemon = True
        # t.start()
        return self

    def stop_stream(self):
        self.idle = True

    def destroy_camera(self):
        pass

    def is_idle(self):
        return self.idle

    def flush_stream(self):
        pass
#        self.camera_buffer.flush()
