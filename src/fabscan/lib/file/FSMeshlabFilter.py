import os
import base64
import logging
import glob

from fabscan.lib.util.FSUtil import json2obj
from fabscan.FSConfig import ConfigInterface
from fabscan.lib.util.FSInject import inject

@inject(
    config=ConfigInterface
)
class FSMeshlabFilter():
    def __init__(self, config):
        self.config = config
        self._logger = logging.getLogger(__name__)

    def get_list_of_meshlab_filters(self):
        basedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        filters = dict()
        filters['filters'] = []
        for file in os.listdir(basedir+"/mlx"):
            if file.endswith(".mlx"):
                if os.path.os.path.exists(basedir+"/mlx/"+file):
                    filter = dict()
                    name, extension = os.path.splitext(file)

                    filter['name'] = name
                    filter['file_name'] = file

                    filters['filters'].append(filter)

        return filters