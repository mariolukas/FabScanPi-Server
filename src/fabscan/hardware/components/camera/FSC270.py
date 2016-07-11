__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import logging
import cv2
import sys, re, threading, collections
import time
from fabscan.FSConfig import Config
from fabscan.FSSettings import Settings
from fabscan.hardware.components.camera.FSAbstractCameraDevice import FSAbstractCameraDevice

class C270(FSAbstractCameraDevice):
    def __init__(self, cambuffer):
        super(C270, self).__init__()

        self._logger =  logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        self.config = Config.instance()
        self.camera_buffer = cambuffer
        self.isRecording = True
        self.timestamp = int(round(time.time() * 1000))
        self.semaphore = threading.BoundedSemaphore()
        self.config = Config.instance()
        self.settings = Settings.instance()

        self.prior_image = None
        self.stream = None

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
