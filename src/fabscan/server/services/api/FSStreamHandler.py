import tornado.ioloop
import tornado.web
import tornado.gen
import time
import logging
import cv2
import numpy as np
import io
from PIL import Image
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorCommand
from fabscan.FSEvents import FSEvents

class FSStreamHandler(tornado.web.RequestHandler):

    def initialize(self, scanprocessor):
        self._logger = logging.getLogger(__name__)
        self.scanprocessor = scanprocessor.start()
        self.types = {
            'laser':       FSScanProcessorCommand.GET_LASER_STREAM,
            'adjustment':  FSScanProcessorCommand.GET_ADJUSTMENT_STREAM,
            'texture':     FSScanProcessorCommand.GET_TEXTURE_STREAM,
            'calibration': FSScanProcessorCommand.GET_CALIBRATION_STREAM
        }


    def getFrame(self, stream_type):
        try:
            if self.scanprocessor.is_alive():
                if stream_type == "laser":
                    img = self.scanprocessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.GET_SETTINGS_STREAM})
                else:
                    img = self.scanprocessor.ask({FSEvents.COMMAND: FSScanProcessorCommand.GET_TEXTURE_STREAM})

                if img is None:
                    img = np.zeros((1, 1, 3), np.uint8)

                ret, jpeg = cv2.imencode('.jpg', img)
            return jpeg.tostring()

        except Exception as e:
           self._logger.warning("Error while trying to trigger the scan processor: " + str(e))


    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
        functionality: generates GET response with mjpeg stream
        input: None
        :return: yields mjpeg stream with http header
        """
        stream_type = self.get_argument('type', True)
        # Set http header fields
        self.set_header('Cache-Control',
                         'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
        self.set_header('Connection', 'close')
        self.set_header('Content-Type', 'multipart/x-mixed-replace;boundary=--boundarydonotcross')
        self.set_header('Connection', 'close')

        try:
            while True:
                # Generating images for mjpeg stream and wraps them into http resp
                img = self.getFrame(stream_type)
                self.write("--boundarydonotcross\n")
                self.write("Content-type: image/jpeg\r\n")
                self.write("Content-length: %s\r\n\r\n" % len(img))
                self.write(img)
                yield tornado.gen.Task(self.flush)
        except Exception as e:
            self._logger.warning('Stream canceled....' + str(e))

    def on_finish(self):
        self.scanprocessor.stop()
