__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
import json
from fabscan.util.FSInject import singleton
import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

class ConfigInterface(object):
    def __init__(self, config, first=True):
        pass


class Config(ConfigInterface):
    def __init__(self, config, first=True):

        if first:
            self.file = config
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

        if not hasattr(self,'texture_illumination'):
            self.texture_illumination = 40

    def save(self):
        current_config = self.todict(self.__dict__)
        with open(self.file, 'w+') as outfile:
            str_ = json.dump(current_config, outfile, indent=4, ensure_ascii=False)
            outfile.write(to_unicode(str_))

    def saveAsFile(self, filename):
        current_config = self.todict(self.__dict__)
        with open(filename, 'w+') as outfile:
            str_ = json.dump(current_config, outfile,  indent=4, ensure_ascii=False)
            outfile.write(to_unicode(str_))

    def todict(self, obj, classkey=None):
            if isinstance(obj, dict):
                data = {}
                for (k, v) in obj.items():
                    data[k] = self.todict(v, classkey)
                return data
            elif hasattr(obj, "_ast"):
                return self.todict(obj._ast())
            elif hasattr(obj, "__iter__"):
                return [self.todict(v, classkey) for v in obj]
            elif hasattr(obj, "__dict__"):
                data = dict([(key, self.todict(value, classkey))
                    for key, value in obj.__dict__.iteritems()
                    if not callable(value) and not key.startswith('_')])
                if classkey is not None and hasattr(obj, "__class__"):
                    data[classkey] = obj.__class__.__name__
                return data
            else:
                return obj

    def update(self, config):
        self.calibration.pattern.rows = config.calibration.pattern.rows
        self.calibration.pattern.columns = config.calibration.pattern.columns
        self.calibration.pattern.square_size = config.calibration.pattern.square_size



@singleton(
    instance=Config
)
class ConfigSingleton(Config):
    def __init__(self, config,instance, first=True ):
        super(Config, self).__init__(self, config, first)
        self.instance = instance