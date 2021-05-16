__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import cv2
import logging
import threading
from fabscan.lib.util.FSInject import inject, singleton
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
import picamera
import time
from picamera.array import PiRGBArray

class PiVideoStream:
    def __init__(self, config, settings, framerate, **kwargs):
        # initialize the camera
        self.camera = picamera.PiCamera()
        time.sleep(2)
        self.camera.awb_mode = 'fluorescent'
        time.sleep(1)

        self.settings = settings
        # set camera parameters
        self.camera.resolution = (config.file.camera.resolution.width, config.file.camera.resolution.height)
        self.preview_resolution = (config.file.camera.preview_resolution.width, config.file.camera.preview_resolution.height)
        self.camera.framerate = framerate

        # set optional camera parameters (refer to PiCamera docs)
        for (arg, value) in kwargs.items():
            setattr(self.camera, arg, value)

        # initialize the stream
        self.rawCapture = PiRGBArray(self.camera, size=(self.camera.resolution.width, self.camera.resolution.height))
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
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

        for fr in self.stream:
            self.camera.contrast = self.settings.file.camera.contrast
            self.camera.brightness = self.settings.file.camera.brightness
            self.camera.brightness = self.settings.file.camera.brightness
            self.camera.saturation = self.settings.file.camera.saturation

            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.high_res_frame = fr.array
            self.low_res_frame = cv2.resize(self.high_res_frame, self.preview_resolution)
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return


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

    def is_idle(self):
        pass

    def flush_stream(self):
        pass
