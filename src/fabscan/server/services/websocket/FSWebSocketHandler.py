import tornado.websocket
from tornado import gen
import json
import sys
import logging
import traceback
from fabscan.FSEvents import FSEvents
from fabscan.lib.util.FSUtil import json2obj
import asyncio

class FSWebSocketHandler(tornado.websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.eventManager = kwargs.pop('eventmanager').instance

        self._logger = logging.getLogger(__name__)

        super(FSWebSocketHandler, self).__init__(*args, **kwargs)
        self.io_loop = tornado.ioloop.IOLoop.instance()

    def check_origin(self, origin):
        return True

    def open(self):
        """
        initilized a new connection. here all config values etc. should be send to client
        """

        self.eventManager.subscribe(FSEvents.ON_SOCKET_BROADCAST, self.on_socket_broadcast)
        self.eventManager.subscribe(FSEvents.ON_SOCKET_SEND, self.on_socket_send)

        message = dict()
        message['client'] = self.request

        self._logger.debug("New client connected")
        self.eventManager.publish(FSEvents.ON_CLIENT_CONNECTED, message)

    def on_message(self, message):
        """
            handles incoming messages from browser and sends it to the bus
         """

        message = json2obj(str(message))
        try:
            # self._logger.debug("Websocket Message received %s" % message.event)
            self.eventManager.publish(message.event, message.data)


        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            self._logger.exception("Runtime error in Websocket message handler: " + str(e))

    def on_close(self):
        """
        is called when a connection is closed. all connection based things should be cleanded here
        """
        self.eventManager.unsubscribe(FSEvents.ON_SOCKET_BROADCAST, self.on_socket_broadcast)
        self.eventManager.unsubscribe(FSEvents.ON_SOCKET_SEND, self.on_socket_send)

        self._logger.debug("Client disconnected")

    @gen.coroutine
    def on_socket_broadcast(self, events, message):

        try:
            self.io_loop.add_callback_from_signal(self.write_message, message)

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            self._logger.exception("Runtime error in Websocket message handler:" + str(e))


    def on_socket_send(self, events, message):

        client = message['data']['client']
        if client and (client == self.request):
            del message['data']['client']

            json_encoded_message = json.dumps(message)
            self.io_loop.add_callback_from_signal(self.write_message, json_encoded_message)
