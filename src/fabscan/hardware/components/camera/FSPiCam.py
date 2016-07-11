__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import sys, re, threading, collections
import time
import picamera
import cv2
import logging
import numpy as np
import io
import traceback
from fabscan.FSConfig import Config
from fabscan.FSSettings import Settings
from fabscan.hardware.components.camera.FSAbstractCameraDevice import FSAbstractCameraDevice

class PiCam(FSAbstractCameraDevice):
    camera = None
    def __init__(self):
        super(PiCam, self).__init__()
        self.start()
        self.isRecording = True
        self.timestamp = int(round(time.time() * 1000))
        self.semaphore = threading.BoundedSemaphore()
        self.camera = None
        self.prior_image = None
        self.stream = None
        self.config = Config.instance()
        self.settings = Settings.instance()
        #self.camera_buffer = cambuffer
        self.awb_default_gain = 0
        self.is_idle = True

        self._logger =  logging.getLogger(__name__)

    def run(self):

        try:
            if(self.camera == None):
                try:
                    self.camera = picamera.PiCamera()
                    self._logger.info("Camera module ready...")
                except:
                    self._logger.error("Can not create camera device.")
                self.awb_default_gain = self.camera.awb_gains
                #self.camera.led = False

                self.camera.resolution = (self.config.camera.resolution.width, self.config.camera.resolution.height)
                #self.camera.framerate = 30
                #self.camera.quality = 70


                self.objectExposureMode()

                self.camera.rotation = self.config.camera.rotation_angle
                #self.camera.vflip = True
                #self.camera.hflip = True

                self._logger.debug("PI Camera Moule ready.")
                while True:

                    if not self.is_idle:
                        stream = io.BytesIO()
                        for foo in self.camera.capture_continuous(stream, format='jpeg', use_video_port=True):

                            self.camera.contrast = self.settings.camera.contrast
                            self.camera.brightness = self.settings.camera.brightness
                            self.camera.saturation = self.settings.camera.saturation
                            stream.seek(0)
                            data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                            data = cv2.imdecode(data, 1)

                            try:
                                self.semaphore.acquire()
                                self.camera_buffer.append(data)
                            finally:
                                self.semaphore.release()
                            stream.truncate()
                            stream.seek(0)

                            if self.is_idle:
                                self.semaphore.acquire()
                                self.is_idle = True
                                self.semaphore.release()
                                break
                    else:
                        time.sleep(0.05)



        except(RuntimeError, TypeError, NameError):
            traceback.print_exc(file=sys.stdout)
            self._logger.debug("Runtime error in camera handler")

        finally:
            self.camera = None
            pass

    def camra_is_connected(self):
        self.isAlive()

    def flushStream(self):
        self.camera_buffer.flush()

    def setPreviewResolution(self):
        pass

    def setScanResolution(self):
        pass

    def textureExposureMode(self):

        #self.camera.exposure_mode = 'auto'
        self.camera.awb_gains = self.awb_default_gain
        self.camera.awb_mode = 'flash'

    def objectExposureMode(self):
        # Wait for analog gain to settle on a higher value than 1
        while self.camera.analog_gain <= 1:
            time.sleep(0.1)
        time.sleep(0.5)


        self.camera.shutter_speed = self.camera.exposure_speed
        self.camera.exposure_mode = 'off'

        g = self.camera.awb_gains
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g


    def setResolution(self, width, height):
        self.camera.resolution = (width, height)

    def getFrame(self):
        return self.camera_buffer.get()

    def startStream(self, first=False):
        try:
            self.semaphore.acquire()
            self.is_idle = False
            #return self.camera_buffer.get()
        finally:
            pass
            self.semaphore.release()

    def stopStream(self):
        self.semaphore.acquire()
        self.is_idle = True
        self.semaphore.release()

    def flushStream(self):

        self.camera_buffer.flush()

    def setContrast(self, contrast):
        pass
        #self.camera.contrast = contrast

    def setBrightness(self, brightness):
        pass
        #self.camera.brightness = brightness