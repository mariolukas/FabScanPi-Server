__author__ = 'mariolukas'

import urllib2
from fabscan.FSVersion import __version__
import logging


def get_latest_version_tag():
    try:
        response = urllib2.urlopen("http://archive.fabscan.org/dists/jessie/main/binary-armhf/Packages").read()
        latest_version = response.splitlines(True)[6].split(" ")[1]
        return latest_version
    except:
        return "0.0.0"

def upgrade_is_available():
    logging.debug("Checking for new Software version...")

    current_version = int(__version__.replace(".", "")[1:])
    latest_version = int(get_latest_version_tag().replace(".", ""))

    if current_version < latest_version:
        return True
    else:
        return False