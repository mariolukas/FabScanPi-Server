__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
import posixpath
import urllib
import time
import socket
from PIL import Image
import StringIO
import re
import base64
from BaseHTTPServer import BaseHTTPRequestHandler
from SimpleHTTPServer import SimpleHTTPRequestHandler
import logging

from fabscan.util.FSUtil import json2obj
from fabscan.server.FSapi import FSapi
from fabscan.vision.FSSettingsPreviewProcessor import FSSettingsPreviewProcessor
from fabscan.FSEvents import FSEventManager, FSEvents
from fabscan.FSConfig import Config
from fabscan.FSScanner import FSCommand



class RequestHandler(SimpleHTTPRequestHandler):

    def __init__(self,*args):
        self._logger =  logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.api = FSapi()
        self._eventManager = FSEventManager.instance()
        self.close_mjpeg_stream = False
        self.config = Config.instance()


        self.ROUTES = (
            # [url_prefix ,  directory_path]
            ['/upload/preview/',''],
            ['/settings.mjpeg',    ''],
            ['/scans',    self.config.folders.scans],
            ['/scan',     self.config.folders.scans],
            ['',          self.config.folders.www],  # empty string for the 'default' match

        )
        try:
            SimpleHTTPRequestHandler.__init__(self, *args)
        except:
            self._logger.info("http socket disconnect")
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
         if None != re.search('/api/v1/scan/preview/add/*', self.path):
            scanID = self.path.split('/')[-1]

            if len(scanID) >0:
                content_len = int(self.headers.getheader('content-length', 0))
                data = self.rfile.read(content_len)
                self.api.save_preview_content(data, scanID)
                self.send_response(200)
                self.end_headers()
            else:
                self.scan_does_not_exist()
                self.end_headers()

    def do_GET(self):

         if None != re.search('/api/v1/scans/*', self.path):

             scan_id = self.path.split('/')[-1]
             # return a full list of all scans
             if len(scan_id) == 0:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(self.api.get_list_of_scans(self.headers))

             # return all information about a scan with given id
             elif len(scan_id) >0:
                # load a scan representation here !
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(self.api.get_scan_by_id(self.headers, scan_id))

         elif None != re.search('/api/v1/delete/*', self.path):

              scan_id = self.path.split('/')[-1]

              if len(scan_id) > 0:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(self.api.delete_scan(self.headers, scan_id))


         elif None != re.search('/stream/*', self.path):

             stream_id = self.path.split('/')[-1]
             if stream_id == 'preview.mjpeg':
                 self.get_stream('CAMERA_PREVIEW')

             elif stream_id == 'texture.mjpeg':
                 self.get_stream('TEXTURE_PREVIEW')

             elif stream_id == 'threshold.mjpeg':
                pass
             else:

                self.stream_does_not_exist()
                self.end_headers()

         else:
            """Serve a GET request."""
            f = self.send_head()
            if f:
                self.copyfile(f, self.wfile)
                f.close()

         return

    def get_stream(self, type):
           self._settingsPreviewProcessor = FSSettingsPreviewProcessor.start()
           self.send_response(200)
           self.send_header('Pragma:', 'no-cache');
           self.send_header('Cache-Control:', 'no-cache')
           self.send_header('Content-Encoding:', 'identify')
           self.send_header('Content-Type','multipart/x-mixed-replace;boundary=--jpgboundary')
           BaseHTTPRequestHandler.end_headers(self)


           try:
                while True:
                    if self.close_mjpeg_stream:
                        self._settingsPreviewProcessor.stop()
                        break

                    if type == 'TEXTURE_PREVIEW':
                        future_image = self._settingsPreviewProcessor.ask({'command': FSEvents.MPJEG_IMAGE,'type':'TEXTURE_PREVIEW'}, block=False)

                    if type == 'THRESHOLD':
                        future_image = self._settingsPreviewProcessor.ask({'command': FSEvents.MPJEG_IMAGE,'type':'THRESHOLD'}, block=False)

                    if type == 'CAMERA_PREVIEW':
                        future_image = self._settingsPreviewProcessor.ask({'command': FSEvents.MPJEG_IMAGE,'type':'CAMERA_PREVIEW'}, block=False)

                    image = future_image.get()


                    if image != None:
                        image = image[:, :, ::-1]
                        stream = Image.fromarray(image)
                        tmpFile = StringIO.StringIO()

                        stream.save(tmpFile,'JPEG')

                        self.wfile.write('--jpgboundary\n\r')
                        self.send_header('Content-Type:','image/jpeg')
                        BaseHTTPRequestHandler.end_headers(self)
                        stream.save(self.wfile,'JPEG')


                    else:
                        time.sleep(0.05)

                self.close_mjpeg_stream = False
                time.sleep(0.05)

           except IOError as e:
                if hasattr(e, 'errno') and e.errno == 32:
                    self.rfile.close()
                    self._settingsPreviewProcessor.stop()
                    return
                else:
                    self._settingsPreviewProcessor.stop()
                    pass


    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers","X-Requested-With, Content-Type")
        BaseHTTPRequestHandler.end_headers(self)

    def scan_does_not_exist(self):
        self.send_response(400, 'Bad Request: record does not exist')
        self.send_header('Content-Type', 'application/json')

    def stream_does_not_exist(self):
        self.send_response(400, 'Bad Request: stream does not exist')
        self.send_header('Content-Type', 'application/json')

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def translate_path(self, path):
        """translate path given routes"""

        # set default root to cwd
        #root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        # look up routes and set root directory accordingly
        for pattern, rootdir in self.ROUTES:
            if path.startswith(pattern):
                # found match!
                path = path[len(pattern):]  # consume path up to pattern len
                root = rootdir
                break

        # normalize path and prepend root directory
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)

        path = root

        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)

        return path

