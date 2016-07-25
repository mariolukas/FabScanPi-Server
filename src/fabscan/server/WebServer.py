__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"


from SocketServer import ThreadingMixIn
import FSHttpRequestHandler
from SocketServer import TCPServer
from BaseHTTPServer import  HTTPServer
from fabscan.FSEvents import FSEventManager
from fabscan.FSConfig import Config
import threading

class ThreadedHTTPServer(ThreadingMixIn, TCPServer):
    pass

class WebServer(ThreadingMixIn,HTTPServer):
    def __init__(self):
        self.eventmanager = FSEventManager.instance()
        self.config = Config.instance()
        handler = FSHttpRequestHandler.CreateRequestHandler(self.eventmanager, self.config)
        HTTPServer.__init__(self, ('',8080),handler)

class FSWebServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        #self._logger = logging.getLogger(__name__)

    def run(self):
        #try:
            #self._logger.info("Webserver started")
            self.webserver = WebServer()
            self.webserver.serve_forever()
        #except:
        #    self._logger.error("WebSocket Crash!")