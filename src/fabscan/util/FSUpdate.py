__author__ = 'mariolukas'

import urllib2
from fabscan.FSVersion import __version__
import logging

def version(v):
    return tuple(map(int, (v.split("."))))

def get_latest_version_tag():
    try:
        response = urllib2.urlopen("http://archive.fabscan.org/dists/jessie/main/binary-armhf/Packages").read()
        line_with_verion_number = 6
        latest_version = response.splitlines(True)[line_with_verion_number].split(" ")[1]
        return latest_version
    except:
        return "0.0.0"

def upgrade_is_available():

    current_version = __version__[2:]
    latest_version = get_latest_version_tag()

    return version(current_version) < version(latest_version)
