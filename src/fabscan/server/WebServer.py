__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"


from SocketServer import ThreadingMixIn
import FSHttpRequestHandler
from SocketServer import TCPServer
from BaseHTTPServer import  HTTPServer



class ThreadedHTTPServer(ThreadingMixIn, TCPServer):
    pass

class WebServer(ThreadingMixIn,HTTPServer):
    def __init__(self):
        HTTPServer.__init__(self, ('',8080), FSHttpRequestHandler.RequestHandler)
