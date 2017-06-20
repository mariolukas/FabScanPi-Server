# $Id: Makefile,v 1.6 2014/10/29 01:01:35 Mario Lukas Exp $
#

PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/fabscanpi-server
PROJECT=fabscanpi-server

all:
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make rpm - Generate a rpm package"
	@echo "make deb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

source:
	$(PYTHON) setup.py sdist $(COMPILE)

install:
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

rpm:
	$(PYTHON) setup.py bdist_rpm --post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

deb:
	# build the source package in the parent directory
	# then rename it to project_version.orig.tar.gz
	#$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../
	#rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
	# build the package
	dpkg-buildpackage -b -uc -us -i -I -rfakeroot

clean:
	$(PYTHON) setup.py clean
	$(MAKE) -f $(CURDIR)/debian/rules clean
	rm -rf build/ MANIFEST
	rm src/fabscan/FSVersion.py
	find . -name '*.pyc' -delete
