__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import json
import sys
import traceback
import logging
from SimpleWebSocketServer import WebSocket
from fabscan.FSEvents import FSEvents, FSEventManagerSingleton
from fabscan.util.FSUtil import json2obj
from fabscan.util.FSInject import inject


@inject(
    eventmanager=FSEventManagerSingleton
)
class FSWebSocket(WebSocket):
    def __init__(self, server, sock, address, eventmanager):
        WebSocket.__init__(self, server, sock, address)

        self._logger = logging.getLogger(__name__)

        self.maxheader = 65536
        self.maxpayload = 4194304
        self.eventManager = eventmanager.instance

        self.eventManager.subscribe(FSEvents.ON_SOCKET_BROADCAST, self.on_socket_broadcast)
        self.eventManager.subscribe(FSEvents.ON_SOCKET_SEND, self.on_socket_send)

    def on_socket_broadcast(self, events, message):

        json_encoded = json.dumps(message)
        try:
            self.sendMessage(json_encoded)
        except (RuntimeError, TypeError, NameError):
            traceback.print_exc(file=sys.stdout)
            self._logger.debug("Runtime error in Websocket message handler")


    def on_socket_send(self, events, message):

        client = message['data']['client']
        if client and (client == self.client):
            del message['data']['client']

            json_encoded = json.dumps(message)
            self.sendMessage(json_encoded)


    def handleMessage(self):
        """
           handles incoming messages from browser and sends it to the bus
        """

        message = json2obj(str(self.data))

        try:
         #self._logger.debug("Websocket Message received %s" % message.event)
         self.eventManager.publish(message.event, message.data)


        except (RuntimeError, TypeError, NameError):
            traceback.print_exc(file=sys.stdout)
            self._logger.debug("Runtime error in Websocket message handler")


    def handleConnected(self):
        """
        initilized a new connection. here all config values etc. should be send to client
        """
        message = dict()
        message['client'] = self.client

        self._logger.debug("New client connected")
        self.eventManager.publish(FSEvents.ON_CLIENT_CONNECTED, message)


    def handleClose(self):
        """
        is called when a connection is closed. all connection based things should be cleanded here
        """
        self.eventManager.unsubscribe(FSEvents.ON_SOCKET_BROADCAST, self.on_socket_broadcast)
        self.eventManager.unsubscribe(FSEvents.ON_SOCKET_SEND, self.on_socket_send)

        self._logger.debug("Client disconnected")
