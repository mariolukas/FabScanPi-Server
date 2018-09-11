__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from fabscan.server import FSScanServer
from fabscan.daemon import Daemon
from fabscan.FSVersion import __version__
import logging
import logging.handlers
import sys


class Main(Daemon):
        def __init__(self, pidfile, configfile, basedir, host, port, debug, allowRoot, logConf):
            Daemon.__init__(self, pidfile)

            self._logger =  logging.getLogger(__name__)
            self._logger.setLevel(logging.DEBUG)
            self._configfile = configfile
            self._basedir = basedir
            self._host = host
            self._port = port
            self._debug = debug
            self._allowRoot = allowRoot
            self._logConf = logConf


        def run(self):
            fabscan = FSScanServer(self._configfile)
            fabscan.run()

def main():

    import argparse

    parser = argparse.ArgumentParser(prog="fabscanpi-server")

    parser.add_argument("-v", "--version", action="store_true", dest="version",
                       help="Output FabScan Pi's version and exit")

    parser.add_argument("-d", "--debug", action="store_true", dest="debug",
                        help="Enable debug mode")

    parser.add_argument("-C", "--camera", action="store", type=str, dest="camera_type",
                        help="Specify the Camera type to use for FabScan Pi")

    parser.add_argument("--host", action="store", type=str, dest="host",
                        help="Specify the host on which to bind the server")
    parser.add_argument("--port", action="store", type=int, dest="port",
                        help="Specify the port on which to bind the server")

    parser.add_argument("-c", "--config", action="store", required=True, dest="config",
                        help="Specify the config file to use. FabScan Pi needs to have write access for the config dialog to work. Defaults to /etc/fabscanpi/default.config.json")

    parser.add_argument("-s", "--settings", required=True, action="store", dest="settings",
                        help="Specify the config file to use. FabScan Pi needs to have write access for the settings dialog to work. Defaults to /etc/fabscanpi/default.settings.json")

    parser.add_argument("--logfile", action="store", dest="logConf", default=None,
                        help="Define the log file and path for logging. Defaults to /var/log/fabscanpi/fabscan.log")

    parser.add_argument("--loglevel", action="store", dest="logLevel", default="debug",
                        help="Specify the Log level. Possible Params are debug, info and warning")

    parser.add_argument("--daemon", action="store", type=str, choices=["start", "stop", "restart"],
                        help="Daemonize/control daemonized FabScan Pi instance (only supported under Linux right now)")

    parser.add_argument("--pid", action="store", type=str, dest="pidfile", default="/tmp/fabscanpi.pid",
                        help="Pidfile to use for daemonizing, defaults to /tmp/fabscanpi.pid")

    parser.add_argument("--iknowwhatimdoing", action="store_true", dest="allowRoot",
                        help="Allow FabScan Pi to fabscanpi-server as user root")

    parser.add_argument("--debugger-host", action="store", dest="debugger_host", default=False,
                        help="Allow to connect to a remote debug server")

    parser.add_argument("--debugger-port", action="store", dest="debugger_port", default=12011, type=int,
                        help="Use port for debug server")

    args = parser.parse_args()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger=logging.getLogger("fabscan")

    if args.debugger_host:
        import pydevd
        pydevd.settrace(args.debugger_host, port=args.debugger_port, stdoutToServer=True, stderrToServer=True)

    log_level= {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING
    }

    level = log_level.get(str(args.logLevel), "debug")
    if args.logConf != None:
        fh=logging.handlers.RotatingFileHandler(args.logConf, maxBytes=5000000, backupCount=5)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.propagate = False
        logger.setLevel(level)
    else:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = False
        logger.setLevel(level)

    if args.version:
        print "FabScan Pi version %s" % __version__
        sys.exit(0)

    try:
        if args.daemon:
            if sys.platform == "darwin" or sys.platform == "win32":
                print >> sys.stderr, "Sorry, daemon mode is only supported under Linux right now"
                sys.exit(2)

            daemon = Main(args.pidfile, args.config, args.basedir, args.host, args.port, args.debug, args.allowRoot, args.logConf)
            if "start" == args.daemon:
                daemon.start()
            elif "stop" == args.daemon:
                daemon.stop()
            elif "restart" == args.daemon:
                daemon.restart()
        else:
            fabscan = FSScanServer(args.config, args.settings)
            fabscan.run()
    except Exception, e:
        logger.fatal("Fatal error: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()