__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import cv2
import logging
import time
import threading
import glob
import inspect
import numpy as np
import os, os.path

from fabscan.lib.util.FSInject import inject, singleton
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.FSEvents import FSEventManagerSingleton, FSEvents, FSEvent
from fabscan.FSScanner import FSCommand

@inject(
    config=ConfigInterface,
    settings=SettingsInterface
)
class DummyVideoStream:
    def __init__(self, config, settings, framerate, eventmanager, **kwargs):
        self._logger = logging.getLogger(__name__)

        self.config = config
        self.settings = settings
        self.framerate = framerate
        self.eventmanager = eventmanager.instance

        self.timestamp = int(round(time.time() * 1000))
        self.frame_count = 0
        self.idle = True
        self.resolution = self.settings.file.resolution
        self.eventmanager.subscribe(FSEvents.COMMAND, self.on_command)
        self.scanner_state = "IDLE"

        self.current_mode_is_preview = True

        self.stopped = False


    def on_command(self, mgr, event):
         command = event.command
         self.scanner_state = command

         if command == "START" or command == "SCAN":
             self.frame_count = 1

         self._logger.debug("dummy command received: {} ".format(command))


    def update(self):
        self._logger.debug("Dummy camera stream started.")
        while not self.stopped:
            time.sleep(0.1)
        self.frame_count = 1

    def get_frame(self, preview=False):

        calframe = inspect.stack()

        if preview:
           self.resolution = 3

        if self.scanner_state == FSCommand.CALIBRATE:
            image_path = self.config.file.camera.image_path + "calibration_6x8"
        else:
            image_path = self.config.file.camera.image_path + "res" + str(self.settings.file.resolution) + "_laser#" + str(self.config.file.laser.numbers)

        frame_count_max = len([name for name in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, name))])

        # if preview mode return only image for first laser.
        if self.config.file.laser.numbers > 1 and preview:
            frame_count_max = frame_count_max / self.config.file.laser.numbers

        # start again...
        if self.frame_count == frame_count_max:
            self.frame_count = 1

        # get image for current count
        for filename in glob.glob(image_path + "/*_{:03d}.jpg".format(self.frame_count)):
            self._logger.debug("frame: {}".format(filename))
            img = cv2.imread(filename, 1)

        # calculate next frame
        if self.scanner_state == FSCommand.CALIBRATE:
            # hacky but works so far
            if calframe[2][3] == "_capture_pattern":
                self._logger.debug(filename)
                self.frame_count += 1
        else:
            # next frame
            if (self.config.file.laser.numbers > 1 and preview):
                self.frame_count += self.config.file.laser.numbers
            else:
                self.frame_count += 1

        if preview:
           low_res_size = (self.config.file.camera.preview_resolution.width, self.config.file.camera.preview_resolution.height)
           img = cv2.resize(img, low_res_size)

        return img

    def start_stream(self):
        self.frame_count = 1
        # start the thread to read frames from the video stream
        t = threading.Thread(target=self.update, name=__name__ + '-Thread', args=())
        t.daemon = True
        t.start()
        self._logger.debug("dummy camera stream started")
        return self

    def stop_stream(self):
        self._logger.debug("dummy camera stream stopped")
        self.stopped = True


@singleton(
    config=ConfigInterface,
    settings=SettingsInterface,
    eventmanager=FSEventManagerSingleton,
)
class FSCameraDummy:

    def __init__(self, config, settings, eventmanager):
        self._logger = logging.getLogger(__name__)
        self.config = config
        self.settings = settings
        self.stream = DummyVideoStream(config=self.config, settings=self.settings, framerate=32, eventmanager=eventmanager)

        self.config = config
        self.settings = settings

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