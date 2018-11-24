import os
import re
import urllib2
import socket

REMOTE_SERVER = "fabscan.org"

import semver
import logging
from fabscan.FSVersion import __version__


__author__ = 'mariolukas'


PACKAGE_PATTERN = re.compile('^Package: fabscanpi-server$')

VERSION_PATTERN = re.compile('^Version: (.+)$')
_logger = logging.getLogger(__name__)

def get_latest_version_tag():

    if is_online(REMOTE_SERVER):
        _logger.debug("Scanner is Online...")
        try:

            response = urllib2.urlopen("http://archive.fabscan.org/dists/stable/main/binary-armhf/Packages", timeout=0.4)
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
    else:
        _logger.debug("Scanner is offline...")
        return __version__

def is_online(hostname):
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False

def upgrade_is_available(current_version):

    latest_version = get_latest_version_tag()

    return semver.compare(latest_version, current_version) == 1, latest_version


def do_upgrade():
    os.system('nohup bash -c "sudo apt-get update -y && sudo apt-get dist-upgrade -y" > /var/log/fabscanpi/upgrade.log')