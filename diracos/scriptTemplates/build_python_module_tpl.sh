#!/bin/bash
# This script is normally called automatically with the arguments taken from the json configuration file

# Exit directly in case of errors
set -e

PIP_BUILD_DEPENDENCIES="%(pipBuildDependencies)s"
PIP_DIRAC=/tmp/pipDirac

echo "Preparing to build python packages"

echo "Pip build dependencies $PIP_BUILD_DEPENDENCIES"

echo "Installing dependency"
yum install $PIP_BUILD_DEPENDENCIES

yum install python2-virtualenv

# We use the --always-copy option in order not to have symlinks to the system.
# However, we cannot just do virtualenv --always-copy /tmp/pipDirac
# See: https://github.com/pypa/virtualenv/issues/565#issuecomment-305002914

mkdir $PIP_DIRAC
cd $PIP_DIRAC
virtualenv --no-pip --no-setuptools .
cd /tmp/

source $PIP_DIRAC/bin/activate

echo "Installing newer pip in virtualenv"
cd /tmp
curl -O -L https://diracos.web.cern.ch/diracos/bootstrap/get-pip.py
python get-pip.py pip==20.2.4

pip install -r /tmp/requirements.txt
virtualenv --relocatable $PIP_DIRAC

# Dump the full list of python packages
pip freeze 2>/dev/null 1> /tmp/pythonPackages.txt
