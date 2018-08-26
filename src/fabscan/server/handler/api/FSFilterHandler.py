import os
import json
import tornado.web


class FSFilterHandler(tornado.web.RequestHandler):

    def get(self):
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

        self.write(json.dumps(filters))