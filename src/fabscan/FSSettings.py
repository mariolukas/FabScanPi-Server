import json
from fabscan.lib.util.FSInject import inject, singleton

class Map(dict):
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        v = Map(v)
                    if isinstance(v, list):
                        self.__convert(v)
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    v = Map(v)
                elif isinstance(v, list):
                    self.__convert(v)
                self[k] = v

    def __convert(self, v):
        for elem in range(0, len(v)):
            if isinstance(v[elem], dict):
                v[elem] = Map(v[elem])
            elif isinstance(v[elem], list):
                self.__convert(v[elem])

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

class SettingsInterface(object):
      def __init__(self, file_name):
        pass

class Settings(SettingsInterface):
    def __init__(self, file_name):
        # concatenation of default and custom dict can be archived by using
        # self.json =  {**loaded_defaults, **loaded_file}
        self.file_name = file_name
        self.file = self.load_json(file_name)
        self.convertToDotDict()

    def convertToDotDict(self):
        self.file = Map(self.file)

    def load_json(self, file):
        with open(file) as json_data_file:
          data = json.load(json_data_file)
          return data

    def save_json(self, file_name=None):
        if file_name:
            destination_file = file_name
        else:
            destination_file = self.file_name
        with open(destination_file, 'w') as outfile:
            json.dump(self.file, outfile, indent=4, ensure_ascii=False)

    def update(self):
        pass

@singleton(
    instance=Settings
)
class SettingsSingleton(Settings):
    def __init__(self, file_name, instance):
        super(Settings, self).__init__(self, file_name)
        self.instance = instance
