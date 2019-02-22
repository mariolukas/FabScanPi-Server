__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
import json
from fabscan.lib.util.FSInject import inject, singleton

class SettingsInterface(object):
      def __init__(self, settings, first=True):
        pass


class Settings(SettingsInterface):

    def __init__(self, settings, first=True):


        if first:
            self.file = settings
            with open(settings) as file:
                settings = file.read()

            settings = json.loads(settings)

        def _traverse(key, element):
            if isinstance(element, dict):
                return key, Settings(element, first=False)
            else:
                return key, element


        object_dict = dict(_traverse(k, v) for k, v in settings.iteritems())

        self.__dict__.update(object_dict)

    def save(self):
        current_settings = self.todict(self.__dict__)

        try:
            del current_settings['file']
        except KeyError:
            pass

        with open(self.file, 'w+') as outfile:
            json.dump(current_settings, outfile, indent=4, ensure_ascii=False)

    def saveAsFile(self, filename):
        current_settings = self.todict(self.__dict__)
        with open(filename, 'w+') as outfile:
            json.dump(current_settings, outfile, indent=4, ensure_ascii=False)

    def update(self, settings):
        self.threshold = settings.threshold
        self.camera.brightness = settings.camera.brightness
        self.camera.contrast = settings.camera.contrast
        self.camera.saturation = settings.camera.saturation
        self.resolution = settings.resolution
        self.color = settings.color
        self.led.blue = settings.led.blue
        self.led.green = settings.led.green
        self.led.red = settings.led.red
        self.show_laser_overlay = settings.show_laser_overlay
        self.show_calibration_pattern = settings.show_calibration_pattern


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

@singleton(
    instance=Settings
)
class SettingsSingleton(Settings):
    def __init__(self, settings, instance):
        super(Settings, self).__init__(self, settings)
        self.instance = instance