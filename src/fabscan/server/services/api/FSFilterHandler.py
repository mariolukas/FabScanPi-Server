import json
from fabscan.lib.file.FSMeshlabFilter import FSMeshlabFilter
from fabscan.server.services.api.FSBaseHandler import BaseHandler

class FSFilterHandler(BaseHandler):

    def initialize(self):
        self.meshlablib = FSMeshlabFilter()

    def get(self):
       filters = self.meshlablib.get_list_of_meshlab_filters()
       self.write(json.dumps(filters))
