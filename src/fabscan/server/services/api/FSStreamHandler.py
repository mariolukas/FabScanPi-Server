import tornado.ioloop
import tornado.web
import tornado.gen
import time
import logging
import cv2
import numpy as np
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorCommand
from fabscan.FSEvents import FSEvents, FSEventManagerSingleton

class FSStreamHandler(tornado.web.RequestHandler):

    def initialize(self, scanprocessor, eventmanager):
        self._logger = logging.getLogger(__name__)
        self.scanprocessor = scanprocessor
        self.eventmanager = eventmanager.get_instance()
        self.served_image_timestamp = 0
        self.stop_mjpeg = False

        self.types = {
            'laser':       FSScanProcessorCommand.GET_LASER_STREAM,
            'adjustment':  FSScanProcessorCommand.GET_ADJUSTMENT_STREAM,
            'texture':     FSScanProcessorCommand.GET_TEXTURE_STREAM,
            'calibration': FSScanProcessorCommand.GET_CALIBRATION_STREAM
        }
        self.eventmanager.subscribe(FSEvents.ON_STOP_MJPEG_STREAM, self.on_mjpeg_stop)

    def on_mjpeg_stop(self, mgr, event):
        self.stop_mjpeg = True

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

                return jpeg.tobytes() #jpeg.tostring()
            else:
                return np.zeros((1, 1, 3), np.uint8)

        except Exception as e:
           self._logger.warning("Error while trying to trigger the scan processor: {0}".format(e))


    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
        functionality: generates GET response with mjpeg stream
        input: None
        :return: yields mjpeg stream with http header
        """
        ioloop = tornado.ioloop.IOLoop.current()
        self._logger.debug("mjpeg stream started.")
        stream_type = self.get_argument('type', True)
        # Set http header fields
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Content-Type', 'multipart/x-mixed-replace;boundary=--jpgboundary')
        self.set_header('Connection', 'close')

        while not self.stop_mjpeg:
            try:
              interval = 1.0
              if self.served_image_timestamp + interval < time.time():
                # Generating images for mjpeg stream and wraps them into http resp
                img = self.getFrame(stream_type)
                if img is None:
                    continue
                self.write("--jpgboundary\r\n")
                self.write("Content-type: image/jpeg\r\n")
                self.write("Content-length: {0}\r\n\r\n".format(len(img)))
                self.write(img)
                self.served_image_timestamp = time.time()
                yield tornado.gen.Task(self.flush)
              else:
                yield tornado.gen.Task(ioloop.add_timeout, ioloop.time() + interval)
            except Exception as e:
                self._logger.warning("mjpeg stream stopped: {0}".format(e))

    def on_finish(self):
        time.sleep(2)
        self.stop_mjpeg = False
        self._logger.debug("Stream Handler Finished.")

