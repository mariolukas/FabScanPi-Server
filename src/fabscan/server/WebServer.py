__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import threading
import FSHttpRequestHandler

from SocketServer import ThreadingMixIn
from SocketServer import TCPServer
from BaseHTTPServer import  HTTPServer
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorInterface
from fabscan.FSConfig import ConfigSingleton, ConfigInterface
from fabscan.util.FSInject import inject

class ThreadedHTTPServer(ThreadingMixIn, TCPServer):
    def __init__(self, config, scanprocessor):
        pass

#class WebServer(ThreadingMixIn, HTTPServer):
class WebServer(HTTPServer):

    def __init__(self, config, scanprocessor):
        handler = FSHttpRequestHandler.CreateRequestHandler(config, scanprocessor)
        HTTPServer.__init__(self, ('', 8080), handler)
        self.exit = False

    def serve_forever(self):
        while not self.exit:
            self.handle_request()

    def kill(self):
        self.exit = True

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

    def run(self):
        self.webserver = WebServer(self.config, self.scanprocessor)
        self.webserver.serve_forever()

    def kill(self):
        self.webserver.kill()