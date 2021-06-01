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

        self.stopped = False


    def on_command(self, mgr, event):
         command = event.command
         self.scanner_state = command


    def update(self):
        while not self.stopped:
            time.sleep(0.1)
        self.frame_count = 0

    def get_frame(self,preview=False):
        #curframe = inspect.currentframe()
        #calframe = inspect.getouterframes(curframe, 2)
        calframe = inspect.stack()
        #self._logger.debug('caller name: {0}'.format(calframe[2][3]))
        # self._logger.debug("SCANNER_STATE: {0}".format(self.scanner_state))
        #  self._logger.debug(self.scanner_state == FSCommand.CALIBRATE)
        if self.scanner_state == FSCommand.CALIBRATE:
            frame_count_max = 133
            image_path = self.config.file.camera.image_path + "calibration_8x10"
        else:
            frame_count_max = 200
            image_path = self.config.file.camera.image_path + str(self.resolution) + "_" + str(self.config.file.laser.numbers)

        if self.frame_count == frame_count_max:
            self.frame_count = 0

        self.resolution = self.settings.file.resolution
        if preview:
            self.resolution = 3

        for filename in glob.glob(image_path + "/*_{:03d}.jpg".format(self.frame_count)):
            # self._logger.debug(filename)
            img = cv2.imread(filename, 1)

        if preview:
            low_res_size = (self.config.file.camera.preview_resolution.width, self.config.file.camera.preview_resolution.height)
            img = cv2.resize(img, low_res_size)

        # check if we need to move on or not (e.g. preview stream should not move on
        # when calibration is running... next frame after frame is processed...
        if self.scanner_state == FSCommand.CALIBRATE:
            if calframe[2][3] == "_capture_pattern":
                self._logger.debug(filename)
                self.frame_count += 1
        else:
            self._logger.debug(filename)
            self.frame_count += 1

        return img

    def start_stream(self):
        self.frame_count = 0
        # start the thread to read frames from the video stream
        t = threading.Thread(target=self.update, name=__name__ + '-Thread', args=())
        t.daemon = True
        t.start()
        return self

    def stop_stream(self):
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