__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import logging
import threading

from SimpleWebSocketServer import SimpleWebSocketServer
from FSWebSocket import WebSocket, FSWebSocket

class FSWebSocketServerInterface(threading.Thread):
    def __init__(self, eventmanager):
        threading.Thread.__init__()
        pass

class FSWebSocketServer(FSWebSocketServerInterface):

    def __init__(self):
        super(FSWebSocketServerInterface, self).__init__(group=None)
        self.port = 8010
        self._logger = logging.getLogger(__name__)

    def run(self):
            self._logger.info("Websocket Server started on port %s" % self.port)
            try:
                self.wsd = SimpleWebSocketServer('', self.port, FSWebSocket)
                self.wsd.serveforever()
            except:
                self._logger.error("Websocket not started")
