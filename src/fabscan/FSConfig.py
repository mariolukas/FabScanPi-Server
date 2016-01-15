__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import logging
import os
import json
from fabscan.util.FSSingleton import SingletonMixin

class Config(SingletonMixin):


    def __init__(self, config=os.path.dirname(__file__)+"/config/default.config.json",first=True):

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

    def update(self):
        pass

    def load(self,file):
        pass