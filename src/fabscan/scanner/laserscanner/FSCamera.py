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

from fabscan.util.FSInject import inject, singleton
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface

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

        if config.camera.type  == 'PICAM':
            self.device = PiCam(self.camera_buffer)

        if config.camera.type == 'dummy':
            self.device = DummyCam()

        if config.camera.type == 'C270':
            self.device = C270(self.camera_buffer)

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
    settings=SettingsInterface
)
class C270(threading.Thread):
    def __init__(self, cambuffer, config, settings):
        threading.Thread.__init__(self)

        self.config = config.instance
        self.settings = settings.instance
        self.camera_buffer = cambuffer
        self.isRecording = True
        self.timestamp = int(round(time.time() * 1000))
        self.semaphore = threading.BoundedSemaphore()

        self.prior_image = None
        self.stream = None

        self._logger =  logging.getLogger(__name__)

        # auto exposure mode for logitech C270 can not be controlled by opencv, with this work
        # around the exposer mode can be set direcly by v4l2
        # a value of 1 deactivates auto exposure
        #subprocess.call(["v4l2-ctl", "--set-ctrl", "exposure_auto=1"])

        try:
            self.camera = cv2.VideoCapture(self.config.camera.device)
        except:
            self._logger.error("Can not create camera device.")
            return

        # this sets the resolution of the C270 which is 1280x720 by default
        self.camera.set(3,1280)
        self.camera.set(4,720)
        self._logger.debug("Selected Camera Device %i" % (int(self.config.camera.device)))
        self.start()

    def run(self):

        try:
            if(self.camera == None):
                sys.exit()

            self._logger.debug("Camera stream started")


            #or foo in self.camera.capture_continuous(stream, format='jpeg', use_video_port=True):
            while True:
                self.camera.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS,self.settings.camera.brightness)
                self.camera.set(cv2.cv.CV_CAP_PROP_CONTRAST,self.settings.camera.contrast)
                _, image = self.camera.read()
                time.sleep(0.1)
                #self.semaphore.acquire()
                self.camera_buffer.append(image)
                #self.semaphore.release()

        finally:
            #subprocess.call(["v4l2-ctl", "--set-ctrl", "exposure_auto=3"])
            self.camera.release()
            self.camera = None
            pass

    def flushStream(self):
        self.camera_buffer.flush()

    def getStream(self, first=False):
        self.timestamp = int(round(time.time() * 1000))
        if(self.isRecording == False):
            self.semaphore.acquire()
            self.isRecording = True
            self.semaphore.release()
            self.run()
        return self.camera_buffer.get()

    def getPreviewImages(self, first=False):
        return self.preview_buffer.get()

    def objectExposure(self):
        pass

    def textureExposure(self):
        pass

    def close(self):
        pass

@inject(
    config=ConfigInterface,
    settings=SettingsInterface
)
class PiCam(threading.Thread):
    camera = None
    def __init__(self, cambuffer, config, settings):
        threading.Thread.__init__(self)
        self.config = config
        self.settings = settings

        self.isRecording = True
        self.timestamp = int(round(time.time() * 1000))
        self.semaphore = threading.BoundedSemaphore()
        self.camera = None
        self.prior_image = None
        self.stream = None
        self.camera_buffer = cambuffer
        self.awb_default_gain = 0
        self.is_idle = True
        self._current_mode = 'custom'
        self._logger = logging.getLogger(__name__)

        self.start()

    def run(self):
        try:
                try:
                    self.camera = picamera.PiCamera()
                    self._logger.info("Camera module ready...")
                except picamera:
                    self._logger.error("Can not create camera device.")

                self.camera.resolution = (self.config.camera.resolution.width, self.config.camera.resolution.height)
                self.camera.framerate = 24

                while True:
                    if not self.is_idle:
                       try:
                            stream = io.BytesIO()
                            for foo in self.camera.capture_continuous(stream, format='jpeg', use_video_port=True):

                                self.camera.contrast = self.settings.camera.contrast
                                self.camera.brightness = self.settings.camera.brightness
                                self.camera.saturation = self.settings.camera.saturation
                                stream.seek(0)

                                self.camera.capture(stream, format='jpeg')
                                # Construct a numpy array from the stream
                                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                                # "Decode" the image from the array, preserving colour
                                image = cv2.imdecode(data, 1)

                                if self.config.camera.rotate == "True":
                                    image = cv2.transpose(image)
                                if self.config.camera.hflip == "True":
                                    image = cv2.flip(image, 1)
                                if self.config.camera.vflip == "True":
                                    image = cv2.flip(image, 0)

                                try:
                                    self.semaphore.acquire()
                                    self.camera_buffer.append(image)
                                finally:
                                    self.semaphore.release()
                                stream.truncate()
                                stream.seek(0)
                       except picamera.PiCameraClosed:
                           self._logger.warning("Camera already closed.")

                    else:

                        time.sleep(0.05)

        except(RuntimeError, TypeError, NameError):
            traceback.print_exc(file=sys.stdout)
            self._logger.debug("Runtime error in camera handler")

        finally:
            self.camera = None
            pass

    def flushStream(self):
        self.camera_buffer.flush()

    def setResolution(self, width, height):
        self.camera.resolution = (width, height)

    def get_resolution(self):
        if self._rotate:
            return int(self.config.camera.resolution.height), int(self.config.camera.resolution.width)
        else:
            return int(self.config.camera.resolution.width), int(self.config.camera.resolution.height)

    def getFrame(self):
        image = None
        while image is None:
           image = self.camera_buffer.get()
        return image

    def startStream(self, auto_exposure=False, exposure_type="flash"):
        self.setExposureMode(auto_exposure=auto_exposure, exposure_type=exposure_type)
        self.semaphore.acquire()
        self.is_idle = False
        self.semaphore.release()

    def stopStream(self):
        self.semaphore.acquire()
        self.is_idle = True
        self.semaphore.release()

    def flushStream(self):
        self.camera_buffer.flush()


    def setExposureMode(self, auto_exposure=False, exposure_type="flash"):
                if not auto_exposure:
                    if self._current_mode is not 'custom':
                        self.camera.iso = 120
                        # Wait for the automatic gain control to settle
                        time.sleep(1.4)
                        # Now fix the values
                        self.camera.shutter_speed = self.camera.exposure_speed
                        self.camera.exposure_mode = 'off'
                        g = self.camera.awb_gains
                        self.camera.awb_mode = 'off'
                        self.camera.awb_gains = g
                        self._current_mode = 'custom'

                else:
                    if self._current_mode is not 'auto':
                        # Now fix the values
                        #self.camera.exposure_mode = exposure_type
                        self.camera.awb_mode = exposure_type
                        time.sleep(1)
                        self._current_mode = 'auto'


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