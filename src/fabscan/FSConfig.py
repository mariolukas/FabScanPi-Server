import json
from fabscan.lib.util.FSInject import inject, singleton
import numpy as np

#https://github.com/BerkeleyAutomation/autolab_core/blob/master/autolab_core/json_serialization.py

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class YAMLobj(dict):
    def __init__(self, args):
        super(YAMLobj, self).__init__(args)
        if isinstance(args, dict):
            for k, v in args.items():
                if not isinstance(v, dict):
                    self[k] = v
                else:
                    self.__setattr__(k, YAMLobj(v))

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(YAMLobj, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(YAMLobj, self).__delitem__(key)
        del self.__dict__[key]


class ConfigInterface(object):
      def __init__(self, file_name):
        pass

class Config(ConfigInterface):
    def __init__(self, file_name):
        # concatenation of default and custom dict can be archived by using
        # self.json =  {**loaded_defaults, **loaded_file}
        self.file_name = file_name
        self.file = self.load_json(file_name)
        self.file = YAMLobj(self.file)

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
