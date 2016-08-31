__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
import json
from fabscan.util.FSInject import singleton


class ConfigInterface(object):
    def __init__(self, config, first=True):
        pass


class Config(ConfigInterface):
    def __init__(self, config, first=True):

        if first:
            with open(config) as file:
                config = file.read()
            config = json.loads(config)

        def _traverse(key, element):
            if isinstance(element, dict):
                return key, Config(element,first=False)
            else:
                return key, element

        object_dict = dict(_traverse(k, v) for k, v in config.iteritems())
        self.__dict__.update(object_dict)

        if not hasattr(self,'scanner_type'):
            self.scanner_type = "laserscanner"

    def update(self):
        pass

    def load(self,file):
        pass


@singleton(
    instance=Config
)
class ConfigSingleton(Config):
    def __init__(self, config,instance, first=True ):
        super(Config, self).__init__(self, config, first)
        self.instance = instance