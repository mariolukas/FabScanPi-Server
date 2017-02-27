import urllib2
import re

import semver


__author__ = 'mariolukas'


PACKAGE_PATTERN = re.compile('^Package: fabscanpi-server$')

VERSION_PATTERN = re.compile('^Version: (.+)$')


def get_latest_version_tag():
    try:
        response = urllib2.urlopen("http://archive.fabscan.org/dists/jessie/main/binary-armhf/Packages")

        latest_version = "0.0.0"
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
    except Exception:
        return "0.0.0"


def upgrade_is_available(current_version):

    latest_version = get_latest_version_tag()

    return semver.compare(latest_version, current_version) == 1, latest_version
