__copyright__ = "Copyright 2020"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import cv2
import logging
import numpy as np
import time

import threading, collections
import picamera
from picamera.array import PiRGBArray
from fabscan.lib.util.FSInject import inject, singleton
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.scanner.interfaces.driver.FSCamera import FSRingBuffer

@singleton(
    config=ConfigInterface,
    settings=SettingsInterface
)
class FSCamera(threading.Thread):
    def __init__(self, config, settings):
        self._logger = logging.getLogger(__name__)

        self.config = config
        self.settings = settings

        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.config.file.camera.resolution.width, self.config.file.camera.resolution.height)
        self.camera.framerate = 30

        self.lowres_frame = None
        self.highres_frame = None

        self.camera_buffer = FSRingBuffer(8)

        time.sleep(2.0)

        self._stop_event = threading.Event()
        self.idle = True
        self.update_thread = None

    def update(self, stop_event, camera, highres_frame):
        t = threading.currentThread()
        _highres_capture = PiRGBArray(self.camera)
        _highres_stream = self.camera.capture_continuous(_highres_capture, format="bgr", use_video_port=True)

        # keep looping infinitely until the thread is stopped
        self._logger.debug("Stream started..")
        while stop_event.isSet():
            lrs = next(_highres_stream)

            #buffer.append(lrs.array)
            self.highres_frame = lrs.array

            _highres_capture.truncate(0)
            _highres_capture.seek(0)

           # hrs = _highres_stream.next()
           # highres_frame = hrs.array
           # _highres_capture.truncate(0)
           # _highres_capture.seek(0)

        self._logger.debug("Stream Stopped.")
        stop_event.clear()

    def get_frame(self):
        frame = None
        # return the frame most recently read

        frame = self.highres_frame
        return frame

    def start_stream(self, mode="default"):
        self.idle = False
        self._stop_event.set()
        # start the thread to read frames from the video stream
        self.update_thread = threading.Thread(target=self.update, args=(self._stop_event, self.camera, self.highres_frame))
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
        #self.camera_buffer.flush()
