__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import cv2
import logging
import numpy as np
import io
import os
import time
import sys, re, threading, collections
import traceback
import PIL

from fabscan.util.FSInject import inject, singleton
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface

try:
	import picamera
except:
	pass


@inject(
    config=ConfigInterface
)
class FSCamera():

    def __init__(self, config):

        self.camera_buffer = FSRingBuffer(10)
        config = config

        if config.camera.type == 'PICAM':
            self.device = PiCam(self.camera_buffer)

        if config.camera.type == 'USBCAM':
            self.device = USBCam(self.camera_buffer)

        if config.camera.type == 'dummy':
            self.device = DummyCam()

    def is_connected(self):
        return self.device.isAlive()


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
        if len(self.data) >= 1:
            image = self.data[-1]
        else:
            image = None
        return image

    def flush(self):
        self.data.clear()

@inject(
    config=ConfigInterface,
    settings=SettingsInterface,
    imageprocessor=ImageProcessorInterface
)
class CamProcessor(threading.Thread):
    def __init__(self, owner, fs_ring_buffer, resolution, mode, config, settings, imageprocessor):
        super(CamProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.config = config
        self.settings = settings
        self.imageprocessor = imageprocessor
        self.imageprocessor.init(resolution)

        self._logger = logging.getLogger(__name__)
        self.owner = owner
        self.mode = mode
        self.fs_ring_buffer = fs_ring_buffer
        self.start()

    def run(self):
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
                    image = cv2.imdecode(data, 1)

                    if self.config.camera.rotate == "True":
                        image = cv2.transpose(image)
                    if self.config.camera.hflip == "True":
                        image = cv2.flip(image, 1)
                    if self.config.camera.vflip == "True":
                        image = cv2.flip(image, 0)

                    if self.mode == "settings":
                        image = self.imageprocessor.get_laser_stream_frame(image)

                    self.fs_ring_buffer.append(image)

                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()

                    # Return ourselves to the available pool
                    with self.owner.lock:
                        self.owner.pool.append(self)

class ProcessCamOutput(object):
    def __init__(self, fs_ring_buffer, resolution, mode="default"):
        self.done = False
        # Construct a pool of 4 image processors along with a lock
        # to control access between threads
        self.lock = threading.Lock()
        self.pool = [CamProcessor(self, fs_ring_buffer, resolution, mode) for i in range(4)]
        self.processor = None
        self._logger = logging.getLogger(__name__)
        self.format_is_mjpeg = True

    def set_no_mjepeg(self):
        self.format_is_mjpeg = False

    def write(self, buf):

        if ((buf[0][0] == 255) and (buf[1][0] == 216)) or buf.startswith(b'\xff\xd8'):
            # New frame; set the current processor going and grab
            # a spare one
            if self.processor:
                self.processor.event.set()
            with self.lock:
                if self.pool:
                    self.processor = self.pool.pop()
                else:
                    # No processor's available, we'll have to skip
                    # this frame; you may want to print a warning
                    # here to see whether you hit this case
                    self.processor = None
        if self.processor:
            self.processor.stream.write(buf)

    def flush(self):
        # When told to flush (this indicates end of recording), shut
        # down in an orderly fashion. First, add the current processor
        # back to the pool
        if self.processor:
            with self.lock:
                self.pool.append(self.processor)
                self.processor = None
        # Now, empty the pool, joining each thread as we go
        while True:
            with self.lock:
                try:
                    proc = self.pool.pop()
                except IndexError:
                    pass # pool is empty
            try:
                proc.terminated = True
                proc.join()
            except StandardError as e:
                pass
            if self.pool.empty:
                break

@inject(
    config=ConfigInterface,
    settings=SettingsInterface
)
class PiCam(threading.Thread):
    camera = None
    def __init__(self, cam_ring_buffer, config, settings):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger(__name__)

        self.config = config
        self.settings = settings
        self.timestamp = int(round(time.time() * 1000))

        self.camera = None
        self.output = None
        #self.resolution = (self.config.camera.preview_resolution.width, self.config.camera.preview_resolution.height)

        self.camera_buffer = cam_ring_buffer
        #self.camera = picamera.PiCamera(resolution=self.resolution)
        self.idle = True
        self.start()


    def run(self):
            while True:
                if not self.idle and self.camera.recording:
                    self.camera.wait_recording(0.5)
                else:
                    time.sleep(0.05)

    def get_frame(self):
        image = None
        while image is None:
           image = self.camera_buffer.get()
        return image

    def set_mode(self, mode):
        camera_mode = {
            "calibration": self.set_calibration_mode,
            "settings": self.set_settings_preview,
            "default": self.set_default_mode,
            "alignment": self.set_alignement_preview
        }
        camera_mode[mode]()

    def set_alignement_preview(self):
        self.resolution = (self.config.camera.preview_resolution.width, self.config.camera.preview_resolution.height)
        self.output = ProcessCamOutput(self.camera_buffer, self.resolution, mode="alignment")

    def set_settings_preview(self):
        self.resolution = (self.config.camera.preview_resolution.width, self.config.camera.preview_resolution.height)
        self.output = ProcessCamOutput(self.camera_buffer, self.resolution, mode="settings")

    def set_default_mode(self):
        self.resolution = (self.config.camera.resolution.width, self.config.camera.resolution.height)
        self.output = ProcessCamOutput(self.camera_buffer, self.resolution)

    def set_calibration_mode(self):
        self.resolution = (self.config.camera.resolution.width, self.config.camera.resolution.height)
        self.output = ProcessCamOutput(self.camera_buffer, self.resolution)

    def start_stream(self, mode="default"):

            try:
                self.set_mode(mode)

                if self.camera is None:
                    self.camera = picamera.PiCamera(resolution=self.resolution)

                self.idle = False
                self.camera.start_recording(self.output, format='mjpeg')
                self._logger.debug("Cam Stream with Resolution "+str(self.resolution)+ " started")
            except StandardError as e:
                self._logger.error("Not able to initialize Raspberry Pi Camera.")
                self._logger.error(e)

    def stop_stream(self):
        time.sleep(0.5)
        try:
            if self.camera.recording:
                self.camera.stop_recording()
            while self.camera.recording:
                time.sleep(0.4)
            self.camera.close()
            self.camera = None
            self.idle = True
            self._logger.debug("Cam Stream with Resolution "+str(self.resolution)+" stopped")

        except StandardError as e:
            self._logger.error("Not able to stop camera.")
            self._logger.error(e)

    def is_idle(self):
        return self.idle

    def flush_stream(self):
        self.camera_buffer.flush()


@inject(
    config=ConfigInterface,
    settings=SettingsInterface
)
class USBCam(threading.Thread):
    camera = None
    def __init__(self, cam_ring_buffer, config, settings):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger(__name__)

        self.config = config
        self.settings = settings
        self.timestamp = int(round(time.time() * 1000))

        self.camera = None
        self.output = None
        self.camera_buffer = cam_ring_buffer
        self.idle = True
        self.start()


    def run(self):
            while True:

                if not self.idle and self.camera.isOpened():
                    try:
                        ret, image = self.camera.read()
                        ret, jpg = cv2.imencode('.jpg', image)
                        self.output.write(jpg)
                    except StandardError, e:
                        pass
                else:
                    time.sleep(0.05)

    def get_frame(self):
        image = None
        while image is None:
           image = self.camera_buffer.get()
        return image

    def set_mode(self, mode):
        camera_mode = {
            "calibration": self.set_calibration_mode,
            "settings": self.set_settings_preview,
            "default": self.set_default_mode,
            "alignment": self.set_alignement_preview
        }
        camera_mode[mode]()

    def set_alignement_preview(self):
        self.resolution = (self.config.camera.preview_resolution.width, self.config.camera.preview_resolution.height)
        self.output = ProcessCamOutput(self.camera_buffer, self.resolution, mode="alignment")

    def set_settings_preview(self):
        self.resolution = (self.config.camera.preview_resolution.width, self.config.camera.preview_resolution.height)
        self.output = ProcessCamOutput(self.camera_buffer, self.resolution, mode="settings")

    def set_default_mode(self):
        self.resolution = (self.config.camera.resolution.width, self.config.camera.resolution.height)
        self.output = ProcessCamOutput(self.camera_buffer, self.resolution)

    def set_calibration_mode(self):
        self.resolution = (self.config.camera.resolution.width, self.config.camera.resolution.height)
        self.output = ProcessCamOutput(self.camera_buffer, self.resolution)

    def start_stream(self, mode="default"):
            self._logger.debug("WebCam Started")
            try:
                self.set_mode(mode)

                if self.camera is None:
                    self.camera = cv2.VideoCapture(0)
                    self.output.format_is_mjpeg = False

                    #HIGHT
                    self.camera.set(3, self.resolution[1])
                    #WIDTH
                    self.camera.set(4, self.resolution[0])

                self.idle = False

                self._logger.debug("Cam Stream with Resolution " + str(self.resolution) + " started")
            except StandardError as e:
                self._logger.error("Not able to initialize USB Camera.")
                self._logger.error(e)

    def stop_stream(self):
        time.sleep(0.5)
        try:
            if self.camera.isOpened():
                self.camera.release()

            self.camera = None
            self.idle = True
            self._logger.debug("Cam Stream with Resolution "+str(self.resolution)+" stopped")

        except StandardError as e:
            self._logger.error("Not able to stop camera.")
            self._logger.error(e)

    def is_idle(self):
        return self.idle

    def flush_stream(self):
        self.camera_buffer.flush()


class DummyCam:

    def __init__(self):
        self.image_count = 1

    def take_picture(self, number=0):
        '''
            dummy camera device loads images from defined dummy folder.
            can be used for simulating a scan without hardware.
        '''

        basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        path = os.path.join(basedir, 'static/data/scans/debug/dummy_img')


        img = None
        i = 1
        for file in os.listdir(path):
            if i == self.image_count:
                file = os.path.join(path, file)
                img = cv2.imread(file)
                break
            i +=1


        self.image_count += 1

        if self.image_count == 214:
            self.image_count = 1
            i = 1
        time.sleep(0.5)
        return img

    def set_exposure(self):
        pass

    def close(self):
        pass