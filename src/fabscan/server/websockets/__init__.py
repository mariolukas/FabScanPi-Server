__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import logging
import threading

from SimpleWebSocketServer import SimpleWebSocketServer
from FSWebSocket import FSWebSocket

class FSWebSocketServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.port = 8010
        self._logger = logging.getLogger(__name__)

    def run(self):
        #try:
            self._logger.info("Websocket Server started on port %s" % self.port)
            self.wsd = SimpleWebSocketServer('', self.port, FSWebSocket)
            self.wsd.serveforever()
        #except:
        #    self._logger.error("WebSocket Crash!")