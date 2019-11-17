import os
import re
import urllib2
import ssl
import socket

REMOTE_SERVER = "fabscan.org"

import semver
import logging
from fabscan.FSVersion import __version__
from fabscan.lib.util.FSUtil import FSSystem


__author__ = 'mariolukas'


PACKAGE_PATTERN = re.compile('^Package: fabscanpi-server$')

VERSION_PATTERN = re.compile('^Version: (.+)$')
_logger = logging.getLogger(__name__)

def get_latest_version_tag():


        try:
            stage = "stable"

            if "+" in __version__:
                stage = "testing"

            if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
                ssl._create_default_https_context = ssl._create_unverified_context

            response = urllib2.urlopen("https://archive.fabscan.org/dists/" + str(stage) + "/main/binary-armhf/Packages", timeout=1)

            latest_version = __version__
            line = 'START'
            while line != '':
                line = response.readline()
                if PACKAGE_PATTERN.match(line):
                    while line != '':
                        line = response.readline()
                        match = VERSION_PATTERN.match(line)
                        if match is not None:
                            package_version = match.group(1)
                            try:
                                if semver.compare(latest_version, package_version) == -1:
                                    latest_version = package_version
                            except ValueError:
                                # ignore invalid version number
                                pass
                            break
            return latest_version
        except (Exception, urllib2.URLError) as e:
            _logger.error(e)
            return __version__



def is_online(host="8.8.8.8", port=53, timeout=1):
  """
  Host: 8.8.8.8 (google-public-dns-a.google.com)
  OpenPort: 53/tcp
  Service: domain (DNS/TCP)
  """
  try:
    socket.setdefaulttimeout(timeout)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    return True
  except socket.error as ex:
    _logger.debug('There is no internet Connection: ' + str(ex))
    return False

def upgrade_is_available(current_version, online_lookup_ip):
    #if is_online(host=online_lookup_ip):
    latest_version = get_latest_version_tag()
    #else:
    #    return __version__

    return semver.compare(latest_version, current_version) == 1, latest_version


def do_upgrade():
    return FSSystem.run_command('sudo apt-get update -y && sudo apt-get install --only-upgrade -y fabscanpi-server" >> /var/log/fabscanpi/upgrade.log', blocking=True)

    #return os.system('sudo apt-get update -y && sudo apt-get install --only-upgrade -y fabscanpi-server" >> /var/log/fabscanpi/upgrade.log')