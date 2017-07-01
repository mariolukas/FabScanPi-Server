__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import os
import posixpath
import urllib
import time
import StringIO
import logging
from PIL import Image
from BaseHTTPServer import BaseHTTPRequestHandler
from SimpleHTTPServer import SimpleHTTPRequestHandler

from fabscan.server.FSapi import FSRest
from fabscan.FSEvents import FSEvents
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorCommand

# parameter is already a config instance
def CreateRequestHandler(config, scanprocessor):

    class RequestHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):

            self.config = config

            self._logger = logging.getLogger(__name__)

            self.api = FSRest()
            self.close_mjpeg_stream = False

            self.scanprocessor = scanprocessor.start()

            self.ROUTES = (
                # [url_prefix ,  directory_path]
                ['/upload/preview/',''],
                ['/settings.mjpeg',    ''],
                ['/scans',    self.config.folders.scans],
                ['/scan',     self.config.folders.scans],
                ['',          self.config.folders.www],  # empty string for the 'default' match

            )
            try:
                SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)
            except StandardError, e:
                self._logger.error(e)

        def do_API_CALL(self, action, data=None):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            json = self.api.call(action, self.path, self.headers, data)
            #self._logger.debug(json)

            self.wfile.write(json)

        def do_DELETE(self):
            if "api" in self.path:
                self.do_API_CALL("DELETE")

        def do_OPTIONS(self):
            self.send_response(200)
            self.end_headers()

        def do_POST(self):
             if "api" in self.path:
                content_len = int(self.headers.getheader('content-length', 0))
                data = self.rfile.read(content_len)
                self.do_API_CALL("POST", data)

        def do_GET(self):

             if "api" in self.path:
                 self.do_API_CALL("GET")

             elif "stream" in self.path:

                 stream_id = self.path.split('/')[-1]
                 if stream_id == 'laser.mjpeg':
                     self.get_stream(FSScanProcessorCommand.GET_LASER_STREAM)

                 elif stream_id == 'texture.mjpeg':
                     self.get_stream(FSScanProcessorCommand.GET_TEXTURE_STREAM)

                 elif stream_id == 'calibration.mjpeg':
                    self.get_stream(FSScanProcessorCommand.GET_CALIBRATION_STREAM)
                 else:

                    self.bad_request()
                    self.end_headers()

             else:
                """Serve a GET request."""
                f = self.send_head()
                if f:
                    self.copyfile(f, self.wfile)
                    f.close()

             return

        def get_stream(self, type):

               self.send_response(200)
               #self.send_header('Pragma:', 'no-cache');
               self.send_header('Cache-Control:', 'no-cache')
               #self.send_header('Content-Encoding:', 'identify')
               self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
               BaseHTTPRequestHandler.end_headers(self)

               try:
                    while True:
                        if self.close_mjpeg_stream:
                            break

                        future_image = self.scanprocessor.ask({FSEvents.COMMAND: type}, block=False)
                        image = future_image.get()

                        if image is not None:
                            image = image[:, :, ::-1]
                            stream = Image.fromarray(image)
                            tmpFile = StringIO.StringIO()

                            stream.save(tmpFile, 'JPEG')

                            self.wfile.write("--jpgboundary\r\n")
                            self.send_header('Content-Type:', 'image/jpeg')
                            self.send_header('Content-length', str(tmpFile.len))
                            BaseHTTPRequestHandler.end_headers(self)
                            stream.save(self.wfile, 'JPEG')
                            self.wfile.write('\r\n')
                            time.sleep(0.5)

                        else:
                            time.sleep(0.05)

                    self.close_mjpeg_stream = False

                    time.sleep(0.05)

               except IOError as e:
                    if hasattr(e, 'errno') and e.errno == 32:
                        self.rfile.close()
                        return
                    else:
                        pass


        def end_headers (self):
            self.send_header('Access-Control-Allow-Origin','*')
            self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS, DELETE, PUT, PATCH')
            self.send_header("Access-Control-Allow-Headers","X-Requested-With, Content-Type")
            BaseHTTPRequestHandler.end_headers(self)

        def bad_request(self):
            self.send_response(400, 'Bad Request: no valid api call')
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
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            return f

        def log_message(self, format, *args):
            self._logger.debug("%s - %s" % (self.client_address[0],format%args))

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

    return RequestHandler