__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"


import abc
import threading, collections

class FSRingBuffer(threading.Thread):

    # Initialize the buffer.
    def __init__(self, size_max):
        self.max = size_max
        self.data = collections.deque(maxlen=size_max)

    # Append an element to the ring buffer.
    def append(self, x):
        if len(self.data) == self.max:
            self.data.pop()
        self.data.append(x)

    # Retrieve the newest element in the buffer.
    def get(self):
        if len(self.data) > 1:
            image = self.data[-1]
        else:
            image = None

        return image

    def flush(self):
        self.data.clear()

class FSAbstractCameraDevice(threading.Thread):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        super(FSAbstractCameraDevice, self).__init__()
        self.camera_buffer = FSRingBuffer(10)
        pass

    def is_connected(self):
        return self.isAlive()

