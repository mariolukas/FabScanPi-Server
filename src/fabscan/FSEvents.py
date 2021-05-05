__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import multiprocessing
import json
from memory_profiler import profile

try:
   from queue import Empty
except ImportError:
   from Queue import Empty

from fabscan.lib.util.FSInject import singleton
import logging

class FSEvent():
    pass

class FSEvents(object):
    ON_CLIENT_CONNECTED = "ON_CLIENT_CONNECTED"
    COMMAND = "COMMAND"
    MPJEG_IMAGE = "MPJEG_IMAGE"
    ON_SOCKET_BROADCAST = "ON_SOCKET_BROADCAST"
    ON_SOCKET_SEND = "ON_SOCKET_SEND"
    ON_NEW_PROGRESS = "ON_NEW_PROGRESS"
    ON_IMAGE_PROCESSED = "ON_IMAGE_PROCESSED"
    ON_STATE_CHANGED = "ON_STATE_CHANGED"
    ON_CLIENT_INIT = "ON_CLIENT_INIT"
    ON_SETTINGS_UPDATED = "ON_SETTINGS_UPDATED"
    ON_SCAN_COMPLETE = "ON_SCAN_COMPLETE"
    ON_NEW_PREVIEW_IMAGE = "ON_NEW_PREVIEW_IMAGE"
    ON_INFO_MESSAGE = "ON_INFO_MESSAGE"
    ON_NET_CONNECT = "ON_NET_CONNECT"
    ON_GET_SETTINGS = "ON_GET_SETTINGS"
    ON_GET_CONFIG = "ON_GET_CONFIG"
    ON_STOP_MJPEG_STREAM = "ON_STOP_MJPEG_STREAM"


class FSEventManagerInterface(object):
     def __init__(self):
         pass

class FSEventManager(FSEventManagerInterface):
    def __init__(self):
        super(FSEventManagerInterface, self).__init__()
        self._logger = logging.getLogger(__name__)
        self.reset()
        self.event_q = multiprocessing.Queue()

    def subscribe(self, key, callback, force=False):

        if key not in self.subscriptions:
            self.subscriptions[key] = []

        subscription = {
            'key': key,
            'callback': callback
        }

        if force or not self.has_subscription(key, callback):
            self.subscriptions[key].append(subscription)

        return self

    def unsubscribe(self, key, callback):
        if not self.has_subscription(key, callback):
            return self

        self.subscriptions[key].remove({
            'key': key,
            'callback': callback
        })

    def unsubscribe_all(self, key):
        if key not in self.subscriptions:
            return self

        self.subscriptions[key] = []

    def has_subscription(self, key, callback):
        if key not in self.subscriptions:
            return False

        subscription = {
            'key': key,
            'callback': callback
        }

        return subscription in self.subscriptions[key]

    def has_any_subscriptions(self, key):
        return key in self.subscriptions and len(self.subscriptions[key]) > 0

    def publish(self, key, *args, **kwargs):
        if not self.has_any_subscriptions(key):
            return self

        for subscriber in self.subscriptions[key]:
            subscriber['callback'](self, *args, **kwargs)

    def send_client_message(self, type, data):
        event_message = dict()
        event_message['type'] = type
        event_message['data'] = data

        self.publish(FSEvents.ON_SOCKET_SEND, event_message)

    def broadcast_client_message(self, type, data):
        event_message = dict()
        event_message['type'] = type
        event_message['data'] = data

        event_message = json.dumps(event_message)
        self.publish(FSEvents.ON_SOCKET_BROADCAST, event_message)

    def reset(self):
        self.subscriptions = {}

    def get_event_q(self):
        return self.event_q


@singleton(
    instance=FSEventManager
)
class FSEventManagerSingleton(FSEventManager):
    def __init__(self, instance):
        super(FSEventManager, self).__init__()
        self.instance=instance

    def get_instance(self):
        return self.instance