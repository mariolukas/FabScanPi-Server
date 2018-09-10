__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import threading

import tornado.ioloop
import tornado.web
import os
import logging
from fabscan.server.services.websocket.FSWebSocketHandler import FSWebSocketHandler
from fabscan.server.services.api.FSFilterHandler import FSFilterHandler
from fabscan.server.services.api.FSScanHandler import FSScanHandler
from fabscan.server.services.api.FSStreamHandler import FSStreamHandler
from fabscan.server.services.api.FSStaticFileHandler import FSStaticFileHandler
from fabscan.FSEvents import FSEvents, FSEventManagerSingleton
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorInterface
from fabscan.FSConfig import ConfigSingleton, ConfigInterface
from fabscan.lib.util.FSInject import inject

@inject(
    config=ConfigInterface,
    scanprocessor=FSScanProcessorInterface,
    eventmanager=FSEventManagerSingleton
)
class FSWebServer(threading.Thread):

    def __init__(self, config, scanprocessor, eventmanager):
        threading.Thread.__init__(self)
        self.config = config
        self.exit = False
        self.scanprocessor = scanprocessor
        self.eventmanager = eventmanager
        self.www_folder = os.path.join(os.path.dirname(__file__), self.config.folders.www)
        self.scan_folder = os.path.join(os.path.dirname(__file__), self.config.folders.scans)
        self._logger = logging.getLogger(__name__)
        self._logger.debug(self.www_folder)

    def routes(self):
        return tornado.web.Application([
            (r"/api/v1/filters/", FSFilterHandler),
            (r"/api/v1/streams/", FSStreamHandler, dict(scanprocessor=self.scanprocessor)),
            (r"/api/v1/scans/", FSScanHandler, dict(config=self.config)),
            (r"/api/v1/scans/(?P<scan_id>\d{8}[-]\d{6}$)", FSScanHandler, dict(config=self.config)),
            (r"/api/v1/scans/(?P<scan_id>\d{8}[-]\d{6})/(?P<files>files)$", FSScanHandler, dict(config=self.config)),
            (r"/api/v1/scans/(?P<scan_id>\d{8}[-]\d{6})/(?P<previews>previews)$", FSScanHandler, dict(config=self.config)),
            (r'/websocket', FSWebSocketHandler, dict(eventmanager=self.eventmanager)),
            (r"/scans/(.*)", FSStaticFileHandler, {"path": self.scan_folder}),
            (r"/(.*)", FSStaticFileHandler, {"path": self.www_folder, "default_filename": "index.html"})
        ])

    def run(self):
        webserver = self.routes()
        webserver.listen(8080)
        tornado.ioloop.IOLoop.current().start()

    def kill(self):
        tornado.ioloop.IOLoop.instance().stop()