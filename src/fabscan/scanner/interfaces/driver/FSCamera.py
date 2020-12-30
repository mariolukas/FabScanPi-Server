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


class FSRingBuffer(threading.Thread):

    # Initialize the buffer.
    def __init__(self, size_max):
        self._logger = logging.getLogger(__name__)
        self.max = size_max
        self.data = collections.deque(maxlen=size_max)
        self.sync = threading.Event()
        #self._lock = threading.RLock()

    # Append an element to the ring buffer.
    def append(self, x):
        #with self._lock:
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