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

@singleton(
    config=ConfigInterface,
    settings=SettingsInterface
)
class FSCamera(threading.Thread):

    def __init__(self, config, settings):
        self._logger = logging.getLogger(__name__)

        self.config = config
        self.settings = settings

        self.stream = cv2.VideoCapture(0)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.file.camera.resolution.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.file.camera.resolution.height)
        #self.stream.set(cv2.CV_CAP_PROP_FPS, 15)
        (self.grabbed, self.frame) = self.stream.read()

        self._stop_event = threading.Event()

        self.idle = True
        self.update_thread = None

    def update(self, stop_event):
        t = threading.currentThread()
        # keep looping infinitely until the thread is stopped
        self._logger.debug("Stream started..")
        while stop_event.isSet():
            (self.grabbed, self.frame) = self.stream.read()
        self._logger.debug("Stream Stopped.")
        stop_event.clear()

    def get_frame(self):
        # return the frame most recently read
        return self.frame

    def start_stream(self, mode="default"):
        self.idle = False
        self._stop_event.set()
        # start the thread to read frames from the video stream
        self.update_thread = threading.Thread(target=self.update, args=(self._stop_event,))
        self.update_thread.daemon = True
        self.update_thread.start()
        return self

    def stop_stream(self):
        self.idle = True
        self._stop_event.clear()

    def destroy_camera(self):
        pass

    def is_idle(self):
        return self.idle

    def flush_stream(self):
        pass
#        self.camera_buffer.flush()
