import urllib.parse, os
import json
import logging
from fabscan.server.services.api.FSStaticFileHandler import FSStaticFileHandler
from fabscan.server.services.api.FSBaseHandler import BaseHandler
from tornado.httpclient import AsyncHTTPClient
import tornado.gen
from tornado.web import HTTPError


class FSDownloadHandler(BaseHandler):

    def initialize(self, *args, **kwargs):
        self.extensions = ['.ply','.stl','.obj','.off','.xyz','.x3d','.3ds']
        self._logger = logging.getLogger(__name__)
        self.config = kwargs.get('config')

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        file_name = kwargs.get('file_name')
        scan_id = kwargs.get('scan_id')
        scan_folder = os.path.join(os.path.join(os.path.dirname(__file__), self.config.file.folders.scans))
        self._logger.debug(file_name)


        _file_dir = "%s/%s" % (scan_folder, scan_id)
        _file_path = "%s/%s" % (_file_dir, file_name)
        if not file_name or not os.path.exists(_file_path):
            raise HTTPError(404)
        self.set_header('Content-Type', 'application/force-download')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % file_name)
        with open(_file_path, "rb") as f:
            try:
                while True:
                    _buffer = f.read(4096)
                    if _buffer:
                        self.write(_buffer)
                    else:
                        f.close()
                        self.finish()
                        return
            except:
                raise HTTPError(404)
        raise HTTPError(500)
