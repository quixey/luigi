# -*- Makefile -*-
# Author: jim@quixey.com

default: help

################################################################################
# Makefile for creating Python virtual environments.
################################################################################

PREFIX = /opt/python27

# Packages we need to build the virtualenv on 12.04
DEB_VIRTUALENV_PACKAGES = python-virtualenv \
                          gcc \
                          python-dev

$(DEB_VIRTUALENV_PACKAGES):
	@sudo apt-get install -y $@

# Create a virtualenv python with $(REQUIREMENTS) packages added to
# the base distribution.

VIRTUAL_LOCATION = $(PREFIX)-luigi
PATH := $(abspath $(VIRTUAL_LOCATION))/bin:$(PREFIX)/bin:$(PATH)

download:
	mkdir download

$(VIRTUAL_LOCATION)/bin/$(PYTHON): download
	@sudo mkdir $(VIRTUAL_LOCATION)
	@sudo chown $(USER) $(VIRTUAL_LOCATION)
	virtualenv $(VIRTUAL_LOCATION)

cleanenv:
	@sudo rm -rf $(VIRTUAL_LOCATION)

requirements: | download
	pip install --download-cache=download --requirement=requirements.txt
	cp requirements.txt $(VIRTUAL_LOCATION)
	git log --decorate requirements.txt > $(VIRTUAL_LOCATION)/requirements.txt.log

# Build luigi from git repo

.PHONY: luigi
luigi:
	[ -d download/luigi ] || git clone git@github.com:quixey/luigi.git download/luigi
	# (cd download/luigi && git checkout 1.0.8)
	(cd download/luigi && python setup.py install)

virtual: cleanenv $(DEB_VIRTUALENV_PACKAGES) $(VIRTUAL_LOCATION)/bin/$(PYTHON) requirements luigi

VERSION = $(shell grep -Po "(?<=version=').*?(?=')" setup.py)

deb: virtual
	fpm -s dir \
			-t deb \
			--force \
			--prefix /\
			--package python27-luigi_$(VERSION).deb \
			--name python27-luigi \
			--category luigi \
			--depends python2.7 \
			--description "Python 2.7 virtualenv for luigi" \
			--deb-user root \
			--deb-group root \
			--version $(VERSION) \
			--url http://github.com/quixey/luigi \
			$(VIRTUAL_LOCATION)

help:
	@echo "type 'make virtual' to create a virtual python environment with the modules:"
	@echo
	@cat requirements.txt
	@echo
	@echo "in the directory $(abspath ../$(VIRTUAL_LOCATION))."
	@echo
	@echo "type 'make deb' to create the file python27-luigi-<VERSION>.deb."
	@echo
