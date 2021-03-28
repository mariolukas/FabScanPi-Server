__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import copy
import cv2
import logging
import numpy as np
import io
import os
import time
import sys, threading, collections
import gc

from fabscan.lib.util.FSInject import inject, singleton
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface
import datetime


class FPS:
    def __init__(self):
        # store the start time, end time, and total number of frames
        # that were examined between the start and end intervals
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        # start the timer
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        # stop the timer
        self._end = datetime.datetime.now()

    def update(self):
        # increment the total number of frames examined during the
        # start and end intervals
        self._numFrames += 1

    def elapsed(self):
        # return the total number of seconds between the start and
        # end interval
        return (self._end - self._start).total_seconds()

    def fps(self):
        # compute the (approximate) frames per second
        return self._numFrames / self.elapsed()


class FSRingBuffer(threading.Thread):

    # Initialize the buffer.
    def __init__(self, size_max):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger(__name__)
        self.max = size_max
        self.data = collections.deque(maxlen=size_max)
        self.sync = threading.Event()
        self.start()
        # self._lock = threading.RLock()

    # Append an element to the ring buffer.
    def append(self, x):
        # with self._lock:
        if len(self.data) == self.max:
            self.data.pop()
        self.data.append(x)

    # Retrieve the newest element in the buffer.
    def get(self):
        if len(self.data) >= 1:
            image = self.data[-1]
        else:
            image = None
        return image

    def isSync(self):
        return self._sync

    def flush(self):
        # with self._lock:
        self.sync.set()
        self.data.clear()
        self.sync.clear()


class FSCamera:

    def __init__(self, config, settings):
        self._logger = logging.getLogger(__name__)
        self.config = config
        self.settings = settings
        self.idle = True

    def get_frame(self, undistort=False):
        return self.stream.read()

    def start_stream(self, mode="default"):
        self.idle = False
        return self.stream.start()

    def stop_stream(self):
        self.idle = True
        self.stream.stop()
