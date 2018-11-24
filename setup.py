 from distutils.core import setup
from setuptools import find_packages
import re
import os
import sys

__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"


sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "src"))


DEPENDENCY_LINKS = []
INSTALL_REQUIRES = []
EXTRA_REQUIRES = dict()


def version_number():
    with open('debian/changelog', 'r') as changelog_file:
        first_line = changelog_file.readline(100)
        result = re.match("fabscanpi-server \(([0-9\.a-z\+]+)\) ([a-zA-Z]+); urgency=([a-z]+)", first_line)
        if result is None:
            return '0.0.0'
        return result.group(1)


def create_version_file():
    with open("src/fabscan/FSVersion.py", "w+") as version_file:
        version_file.write('__version__ = "%s"\n ' % str(version_number()))

create_version_file()


def package_data_dirs(source, sub_folders):
	import os
	dirs = []

	for d in sub_folders:
		folder = os.path.join(source, d)
		if not os.path.exists(folder):
			continue

		for dirname, _, files in os.walk(folder):
			dirname = os.path.relpath(dirname, source)
			for f in files:
				dirs.append(os.path.join(dirname, f))

	return dirs




def params():

    version = str(version_number())
    name = "FabScanPi"
    description = "FabScanPi is a Stand-alone Web-enabled Open-Source 3D Laser Scanner Software"
    long_description = open("README.md").read()
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: JavaScript",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Printing",
        "Topic :: System :: Networking :: Monitoring"
    ]
    author = "Mario Lukas"
    author_email = "info@mariolukas.de"
    url = "http://www.fabscan.org"
    license = "AGPLv3"


    packages = find_packages(where="src")
    package_dir = {
        "": "src"
    }


    include_package_data = True
    zip_safe = False
    install_requires = INSTALL_REQUIRES
    extras_require = EXTRA_REQUIRES
    dependency_links = DEPENDENCY_LINKS

    if os.environ.get('READTHEDOCS', None) == 'True':
        # we can't tell read the docs to please perform a pip install -e .[develop], so we help
        # it a bit here by explicitly adding the development dependencies, which include our
        # documentation dependencies
        install_requires = install_requires + extras_require['develop']


    data_files = [
        ('/etc/sudoers.d/', ['debian/fabscanpi-sudoers']),
        ('/etc/fabscanpi/', ['src/fabscan/config/default.settings.json']),
        ('/etc/fabscanpi/', ['src/fabscan/config/default.config.json']),
        ('/usr/share/fabscanpi/', ['src/www/index.html']),
        ('/usr/share/fabscanpi/style/',['src/www/style/app.css', 'src/www/style/lib.css']),
        ('/usr/share/fabscanpi/js/',['src/www/js/app.js', 'src/www/js/lib.js']),
        ('/usr/share/fabscanpi/js/locales/en/',['src/www/js/locales/en/i18n.js']),
        ('/usr/share/fabscanpi/locales/de/',['src/www/js/locales/de/i18n.js']),
        ('/usr/share/fabscanpi/icons/', ['src/www/icons/icon_mesh.svg','src/www/icons/icon_scan.svg','src/www/icons/icon_pointcloud.svg','src/www/icons/favicon.png', 'src/www/icons/spinner.gif', 'src/www/icons/logo.png']),
        ('/usr/share/fabscanpi/fonts/', ['src/www/fonts/fontawesome-webfont.woff2', 'src/www/fonts/fontawesome-webfont.woff', 'src/www/fonts/fontawesome-webfont.ttf']),
        ('/usr/share/fabscanpi/style/fonts/', ['src/www/style/fonts/slick.woff', 'src/www/style/fonts/slick.ttf'])

    ]

    scripts=['src/fabscanpi-server']


    return locals()

setup(**params())
