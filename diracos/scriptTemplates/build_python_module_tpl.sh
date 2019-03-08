#!/bin/bash
# This script is normally called automatically with the arguments taken from the json configuration file

PIP_BUILD_DEPENDENCIES="%(pipBuildDependencies)s"
PIP_DIRAC=/tmp/pipDirac

echo "Installing pip"
cd /tmp
curl -O -L https://bootstrap.pypa.io/get-pip.py
python get-pip.py

echo "Preparing to build pythong packages"

echo "Pip build dependencies $PIP_BUILD_DEPENDENCIES"

echo "Installing dependency"
yum install $PIP_BUILD_DEPENDENCIES

yum install python2-virtualenv

# We use the --always-copy option in order not to have symlinks to the system.
# However, we cannot just do virtualenv --always-copy /tmp/pipDirac
# See: https://github.com/pypa/virtualenv/issues/565#issuecomment-305002914

mkdir $PIP_DIRAC
cd $PIP_DIRAC
virtualenv .
cd /tmp/

source $PIP_DIRAC/bin/activate
pip install -r /tmp/requirements.txt
virtualenv --relocatable $PIP_DIRAC

# Dump the full list of python packages
pip freeze 2>/dev/null 1> /tmp/pythonPackages.txt
