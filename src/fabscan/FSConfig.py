import json
import numpy as np
from fabscan.lib.util.FSInject import inject, singleton
from fabscan.lib.util.FSJson import YAMLobj,  NumpyEncoder
import logging
import math

class ConfigInterface(object):
      def __init__(self, file_name):
        pass

class Config(ConfigInterface):
    def __init__(self, file_name):
        self._logger = logging.getLogger(__name__)
        self.file_name = file_name
        self.file = self.load_json(file_name)
        self.file = YAMLobj(self.file)
        self.low_weighted_matrix = np.array([])
        self.high_weighted_matrix = np.array([])

    def load_json(self, file):
        self._logger.debug("Loading config file.")
        with open(file) as json_data_file:
            data = json.load(json_data_file)
            # fill config with default values when not set
            self._logger.debug("Checking for valid config values.")

            if 'type' not in data['calibration']:
                data['calibration']['type'] = "chessboard"

            if 'keep_calibration_raw_images' not in data:
                data['keep_calibration_raw_images'] = False

            if 'keep_raw_images' not in data:
                data['keep_raw_images'] = False

            if 'height' not in data['turntable']:
                data['turntable']['height'] = 155

            # turntable resolution defaults
            if 'degree_per_step' not in data['turntable']:
                data['turntable']['degree_per_step'] = dict()
                if 'low' not in data['turntable']['degree_per_step']:
                    data['turntable']['degree_per_step']['low'] = 3.6

                if 'medium' not in data['turntable']['degree_per_step']:
                    data['turntable']['degree_per_step']['medium'] = 1.8

                if 'high' not in data['turntable']['degree_per_step']:
                    data['turntable']['degree_per_step']['high'] = 0.8

            return data

    def keys_exists(self, element, *keys):
        '''
        Check if *keys (nested) exists in `element` (dict).
        '''
        if not isinstance(element, dict):
            raise AttributeError('keys_exists() expects dict as first argument.')
        if len(keys) == 0:
            raise AttributeError('keys_exists() expects at least two arguments, one given.')

        _element = element
        for key in keys:
            try:
                _element = _element[key]
            except KeyError:
                return False
        return True

    def save_json(self, file_name=None):
        if file_name:
            destination_file = file_name
        else:
            destination_file = self.file_name

        with open(destination_file, 'w') as outfile:
            json.dump(self.file, outfile, cls=NumpyEncoder, indent=4, ensure_ascii=False)

    def update(self):
        pass

@singleton(
    instance=Config
)
class ConfigSingleton(Config):
    def __init__(self, file_name, instance):
        super(Config, self).__init__(self, file_name)
        self.instance = instance

