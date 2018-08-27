import os
import json
from fabscan.server.services.api.FSBaseHandler import FSBaseHandler

class FSFilterHandler(FSBaseHandler):

    def get(self):
       filters = self.get_list_of_meshlab_filters()
       self.write(json.dumps(filters))

    def get_list_of_meshlab_filters(self):
        basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

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