import subprocess
import logging
import tornado.web
import time
from os.path import basename
from datetime import datetime
from zipfile import ZipFile
from fabscan.lib.file.FSScans import FSScans
from fabscan.server.services.api.FSBaseHandler import BaseHandler


class FSLogHandler(BaseHandler):


    def initialize(self, *args, **kwargs):
        self._logger = logging.getLogger(__name__)
        self.config = kwargs.get('config')
        self.scanlib = FSScans()


    @tornado.web.asynchronous
    def get(self):
        try:
            log_file = self._logger.handlers[0].baseFilename
        except:
            log_file = "/var/log/fabscanpi/fabscanpi.log"

        timestamp = datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
        if "download" in self.request.path:
            zip_file = "/tmp/fanbscanpi-debug-" + timestamp + ".zip"
            config_file = "/etc/fabscanpi/default.config.json"
            settings_file = "/etc/fabscanpi/default.settings.json"
            process_list = "/tmp/process_list.txt"
            cpu_info = "/tmp/cpu_info.txt"
            voltage_monitor = "/tmp/voltage_state.txt"

            process = subprocess.Popen(["ps -axf > " + process_list], shell=True, stdout=subprocess.PIPE)
            process.wait()

            process = subprocess.Popen(["cat /proc/cpuinfo > " + cpu_info], shell=True, stdout=subprocess.PIPE)
            process.wait()

            process = subprocess.Popen(["vcgencmd get_throttled > " + voltage_monitor], shell=True, stdout=subprocess.PIPE)
            process.wait()

            # put all debug files to zip
            with ZipFile(zip_file, 'w') as log_zip:
                log_zip.write(log_file, basename(log_file))
                log_zip.write(config_file, basename(config_file))
                log_zip.write(settings_file, basename(settings_file))
                log_zip.write(process_list, basename(process_list))
                log_zip.write(cpu_info, basename(cpu_info))
                log_zip.write(voltage_monitor, basename(voltage_monitor))

            buf_size = 4096
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename='+basename(zip_file))

            with open(zip_file, 'r') as f:
                while True:
                    data = f.read(buf_size)
                    if not data:
                        break
                    self.write(data)

            self.finish()

        if "show" in self.request.path:
            try:
                self.p = subprocess.Popen( ["tail", "-f", log_file, "-n+1"], stdout=subprocess.PIPE)
                self.write("<pre>")
                self.flush()
                self.stream = tornado.iostream.PipeIOStream(self.p.stdout.fileno())
                self.stream.read_until("\n", self.line_from_nettail)
            except:
                self.write("No log path configured. Default logging to stdout is active.<br>")
                self.write("For seeing a log output here you need to configure a log file path.<br>")
                self.flush()
                self.finish()

    def on_connection_close(self, *args, **kwargs):
        """Clean up the nettail process when the connection is closed.
        """
        self.p.terminate()
        tornado.web.RequestHandler.on_connection_close(self, *args, **kwargs)

    def line_from_nettail(self, data):
        self.write(data)
        self.flush()
        self.stream.read_until("\n", self.line_from_nettail)