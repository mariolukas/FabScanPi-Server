import os
import re
import urllib.request, urllib.error, urllib.parse
import ssl
import socket

REMOTE_SERVER = "archive.fabscan.org"

import semver
import logging
from fabscan.FSVersion import __version__

__author__ = 'mariolukas'


PACKAGE_PATTERN = re.compile('^Package: fabscanpi-server$')

VERSION_PATTERN = re.compile('^Version: (.+)$')
_logger = logging.getLogger(__name__)

def get_build(version):
    match = semver._REGEX.match(version)
    if match is None:
        raise ValueError('%s is not valid SemVer string' % version)

    verinfo = match.groupdict()

    return int(verinfo['build'])

def get_stage(version):
    if "+" in version:
        return "testing"
    else:
        return "stable"

def is_testing(version):
    return get_stage(version) == 'testing'

def new_build_available(latest_version, package_version):
    return get_build(latest_version) < get_build(package_version)

def get_latest_version_tag():

        try:
            stage = get_stage(__version__)

            if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
                ssl._create_default_https_context = ssl._create_unverified_context

            response = urllib.request.urlopen("https://"+REMOTE_SERVER+"/dists/" + str(stage) + "/main/binary-armhf/Packages", timeout=1)

            latest_version = __version__
            line = 'START'
            while line != '':
                line = response.readline().decode('utf-8')
                if PACKAGE_PATTERN.match(line):
                    while line != '':
                        line = response.readline().decode('utf-8')
                        match = VERSION_PATTERN.match(line)
                        if match is not None:

                            package_version = match.group(1)
                            try:

                                if semver.compare(latest_version, package_version) == -1:
                                    latest_version = package_version

                                if is_testing() and semver.compare(latest_version, package_version) == 0 and new_build_available(latest_version, package_version):
                                    latest_version = package_version

                            except ValueError:
                                # ignore invalid version number
                                pass
                            break

            return latest_version
        except (Exception, urllib.error.URLError) as e:
            _logger.error("Error while getting latest version tag: " + str(e))
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


def is_upgradeable(latest_version, current_version):
    _new_version_available = semver.compare(latest_version, current_version) == 1
    _new_build_available = False

    if is_testing():
        _new_build_available = (semver.compare(latest_version, current_version) == 0) and new_build_available(
            current_version, latest_version)

    return _new_version_available or _new_build_available


def upgrade_is_available(current_version, online_lookup_ip):
    if is_online(host=online_lookup_ip):
        latest_version = get_latest_version_tag()
    else:
        return __version__

    return is_upgradeable(latest_version, current_version), latest_version


def do_upgrade():
    try:
        os.system(
            'nohup bash -c "sudo apt-get update -y && sudo apt-get install -y --only-upgrade -o Dpkg::Options::=\'--force-confnew\' fabscanpi-server > /var/log/fabscanpi/upgrade.log"')
    except Exception as e:
        logging.error("Error while update" + str(e))

