__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import threading

import tornado.ioloop
import tornado.web
import os

from fabscan.server.services.websocket.FSWebSocketHandler import FSWebSocketHandler
from fabscan.server.services.api.FSFilterHandler import FSFilterHandler
from fabscan.server.services.api.FSScanHandler import FSScanHandler
#from fabscan.server.services.api.FSLaserStreamHandler import FSLaserStreamHandler
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorInterface
from fabscan.FSConfig import ConfigSingleton, ConfigInterface
from fabscan.util.FSInject import inject

@inject(
    config=ConfigInterface,
    scanprocessor=FSScanProcessorInterface
)
class FSWebServer(threading.Thread):

    def __init__(self, config, scanprocessor):
        threading.Thread.__init__(self)
        self.config = config
        self.exit = False
        self.scanprocessor = scanprocessor
        self.www_folder = os.path.join(os.path.dirname(__file__), self.config.folders.www)

    def routes(self):
        return tornado.web.Application([
            (r"/api/v1/filters/", FSFilterHandler),
#            (r"/api/v1/stream/laser.mjpeg", FSLaserStreamHandler),
            (r"/api/v1/scans/", FSScanHandler, dict(config=self.config)),
            (r"/api/v1/scans/([0 - 9]+)", FSScanHandler, dict(config=self.config)),
            (r'/ws', FSWebSocketHandler),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": self.www_folder, "default_filename": "index.html"})
        ])

    def run(self):
        webserver = self.routes()
        webserver.listen(8080)
        tornado.ioloop.IOLoop.current().start()

    def kill(self):
        tornado.ioloop.IOLoop.instance().stop()