__author__ = 'mariolukas'

import urllib2
import json
from fabscan.FSConfig import Config
from fabscan.FSVersion import __version__
import logging


def get_latest_version_tag():
    try:
        response = urllib2.urlopen("https://api.github.com/repos/mariolukas/FabScanPi-Server/tags").read()
        tags = json.loads(response)
        return tags[0]['name']
    except:
        return "v.0.0.0"

def upgrade_is_available():
    logging.debug("Checking for new Software version...")
    current_version = int(__version__.replace(".", "")[1:])
    latest_version = int(get_latest_version_tag().replace(".", "")[1:])

    if current_version <= latest_version:
        return True
    else:
        return False