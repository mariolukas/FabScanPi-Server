__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import cv2
import logging
import numpy as np
import io
import time
import threading
import gc

from fabscan.lib.util.FSInject import inject, singleton
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface
from fabscan.scanner.interfaces.driver.FSCamera import FSRingBuffer, FPS
import picamera

NUMBER_OF_CAMERA_THREADS=1

@inject(
    config=ConfigInterface,
    settings=SettingsInterface,
    imageprocessor=ImageProcessorInterface
)
class CamProcessor(threading.Thread):
    def __init__(self, owner, high_res_buffer, low_res_buffer, config, settings, imageprocessor):
        super(CamProcessor, self).__init__()
        self._logger = logging.getLogger(__name__)

        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.config = config
        self.settings = settings
        self.imageprocessor = imageprocessor
        self.owner = owner
        self.high_res_buffer = high_res_buffer
        self.low_res_buffer = low_res_buffer
        self.start()

    def create_low_res_image(self, image):
        low_res_size = (self.config.file.camera.preview_resolution.width, self.config.file.camera.preview_resolution.height)
        image = cv2.resize(image, low_res_size)
        return image

    def run(self):
        # This method runs in a separate thread
        self._logger.debug("Cam Processor Thread with id {0} started.".format(threading.get_ident()))
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    image = np.fromstring(self.stream.getvalue(), dtype=np.uint8)

                    image = cv2.imdecode(image, 1)

                    resolution = image.shape[:2]
                    #newcameramtx, roi = cv2.getOptimalNewCameraMatrix(np.matrix(self.config.file.calibration.camera_matrix), np.matrix(self.config.file.calibration.distortion_vector), resolution, 0, resolution)

                    #image = cv2.undistort(image, np.matrix(self.config.file.calibration.camera_matrix), np.matrix(self.config.file.calibration.distortion_vector), None, np.matrix(newcameramtx))
                    #mapx, mapy = cv2.initUndistortRectifyMap(np.matrix(self.config.file.calibration.camera_matrix), np.matrix(self.config.file.calibration.distortion_vector), None, np.matrix(self.config.file.calibration.camera_matrix), resolution, 5)
                    #img = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)

                    low_res_image = self.create_low_res_image(image)

                    self.high_res_buffer.append(image)
                    self.low_res_buffer.append(low_res_image)

                except Exception as e:
                    # we have an image but another kind of error.
                    if image:
                        self._logger.error(e)
                    pass

                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()

                    # Return ourselves to the available pool
                    with self.owner.lock:
                        self.owner.pool.append(self)
        self._logger.debug("Cam Processor Thread with id {0} killed.".format(threading.get_ident()))


class ProcessCamOutput():
    def __init__(self, high_res_buffer, low_res_buffer):
        self.done = False
        # Construct a pool of 4 image processors along with a lock
        # to control access between threads
        self.lock = threading.Lock()
        self.pool = [CamProcessor(self, high_res_buffer, low_res_buffer) for i in range(NUMBER_OF_CAMERA_THREADS)]

        self.processor = None
        self._logger = logging.getLogger(__name__)
        self.format_is_mjpeg = True

    def write(self, buf):
        try:
            if buf.startswith(b'\xff\xd8'):
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
        except Exception as err:
            # self._logger.error("Error whie writing the buffer: " + str(err))
            pass

    def flush(self):
        # When told to flush (this indicates end of recording), shut
        # down in an orderly fashion. First, add the current processor
        # back to the pool
        for process in self.pool:
            process.terminated = True
        time.sleep(0.2)

        if self.processor:
            with self.lock:
                self.pool.append(self.processor)

        for proc in self.pool:
            proc.terminated = True

        for proc in self.pool:
            proc.join()


@singleton(
    config=ConfigInterface,
    settings=SettingsInterface
)
class FSCameraPi(threading.Thread):

    def __init__(self, config, settings):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger(__name__)

        self.config = config
        self.settings = settings
        self.timestamp = int(round(time.time() * 1000))

        self.camera = None
        self.output = None

        self.capture_stream = io.BytesIO()
        self.high_res_buffer = FSRingBuffer(3)
        self.low_res_buffer = FSRingBuffer(3)

        self.idle = True
        self.resolution = (
        self.config.file.camera.resolution.width, self.config.file.camera.resolution.height)
        self.camera = picamera.PiCamera(resolution=self.resolution)

        self.camera.framerate = 30
        # Wait for the automatic gain control to settle
        self.start()

    def run(self):
        while True:
            if self.camera and not self.idle and self.camera.recording:
                try:
                    self.camera.wait_recording(0.1)
                    self.camera.contrast = self.settings.file.camera.contrast
                    self.camera.brightness = self.settings.file.camera.brightness
                    self.camera.brightness = self.settings.file.camera.brightness
                    self.camera.saturation = self.settings.file.camera.saturation

                except Exception as err:
                    self._logger.error("Error while camera is recording: {0}".format(err))
                    pass

            else:
                time.sleep(0.05)

    def get_frame(self, preview=False):
        image = None
        while image is None:
            if preview:
               image = self.low_res_buffer.get()
            else:
               image = self.high_res_buffer.get()

        return image

    def start_stream(self, mode="default"):

        if self.is_idle():
            try:
                self.output = ProcessCamOutput(self.high_res_buffer, self.low_res_buffer)

                if self.camera:
                    self.camera.resolution = self.resolution
                    # self.camera.awb_mode = 'auto'
                    # self.camera.iso = 200
                    # self.camera.shutter_speed = 10000
                    # time.sleep(1)
                    # g = self.camera.awb_gains
                    # self.camera.awb_mode = 'off'
                    # self.camera.awb_gains = g

                    self.idle = False
                    self.camera.start_recording(self.output, format='mjpeg')
                    self._logger.debug("Cam Stream with Resolution {0} started".format(self.resolution))
            except Exception as e:
                self._logger.error("Not able to initialize Raspberry Pi Camera. {0}".format(e))
                self._logger.error(e)

    def stop_stream(self):
        if not self.idle:
            try:
                if self.camera.recording:
                    self.camera.stop_recording()
                    self.output.flush()
                    self.output = None
                    gc.collect()

                while self.camera.recording:
                    time.sleep(0.05)

                self.idle = True
                self._logger.debug("Cam Stream with Resolution {0} stopped".format(self.resolution))

            except Exception as e:
                self._logger.error("Not able to stop camera: {0}".format(e))
                self._logger.error(e)

    def destroy_camera(self):
        if self.camera:
            self.camera.close()
            self.camera = None

    def is_idle(self):
        return self.idle

    def flush_stream(self):
        self.high_res_buffer.flush()
        self.low_res_buffer.flush()
