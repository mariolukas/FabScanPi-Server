import json
from fabscan.lib.util.FSInject import inject, singleton
from fabscan.lib.util.FSJson import YAMLobj,  NumpyEncoder

class SettingsInterface(object):
      def __init__(self, file_name):
        pass

class Settings(SettingsInterface):
    def __init__(self, file_name):
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

    def update(self, values):

        self.file = YAMLobj(values)

@singleton(
    instance=Settings
)
class SettingsSingleton(Settings):
    def __init__(self, file_name, instance):
        super(Settings, self).__init__(self, file_name)
        self.instance = instance
