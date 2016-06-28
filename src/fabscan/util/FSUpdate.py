__author__ = 'mariolukas'

import urllib2
import json
from fabscan.FSConfig import Config
from fabscan.FSVersion import __version__


def get_latest_version_tag():
    response = urllib2.urlopen("https://api.github.com/repos/mariolukas/FabScanPi-Server/tags").read()
    tags = json.loads(response)
    return tags[0]['name']

def is_up_to_date():
    if __version__ <= get_latest_version_tag():
        return False
    else:
        return True