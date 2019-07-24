#!/bin/bash

# This template will:
# * download a specific version of DIRACOS
# * extract it and use its environment
# * Install with pip the new packages
# * Generate a new versions files containing the extra packages
# * Generate a new archive file

# Exit directly in case of errors
set -e

# name of the extension e.g. LHCb
EXTENSION_NAME=%(extensionName)s
# Version of DIRACOS on which to base the extension (e.g. 'master')
DIRACOS_VERSION=%(diracOsVersion)s
# Version of the extension that we are building
DIRACOS_EXT_VERSION=%(diracOsExtVersion)s

# The temporary location is created by XXX
# Note: we do not use TMPDIR because it is
# already used by standard tools
TMPLOC=%(tmpDir)s

# Location where the building takes place
DIRACOS_EXT=$TMPLOC

# Name of the requirements.txt file
# It should have been placed there by XXX
PIP_EXT_FILE="$DIRACOS_EXT/requirements.txt"

# Path of DIRACOS that we will use
DIRACOS_PATH=$DIRACOS_EXT/diracos
# Name of the version files we have to generate
DIRACOS_EXT_VERSION_FILE=$DIRACOS_PATH/"$EXTENSION_NAME"_versions.txt


# In principle not needed because already created by XXX
mkdir -p $DIRACOS_EXT
cd $DIRACOS_EXT

# Downloading the base DIRACOS to rely on it

DIRACOS_URL="https://diracos.web.cern.ch/diracos/releases/diracos-"$DIRACOS_VERSION".tar.gz"

echo "Downloading base DIRACOS $DIRACOS_VERSION from $DIRACOS_URL"

curl -L $DIRACOS_URL | tar xzf -

# Note: ideally, you would want to do the next operations in a different
# shell since you are about to source diracosrc
# But it is cumbersome, so we will not do it, and hope
# that the tar command will always work

echo "Sourcing diracosrc"
source $DIRACOS_PATH/diracosrc



echo "Dumping list of packages before extension"
pip freeze | sort > before.txt

echo "Installing new python packages"
pip install -r $PIP_EXT_FILE


echo "Dumping list of packages after extension"
pip freeze | sort > after.txt


# add the list of python packages for info
echo "Adding the version list $DIRACOS_EXT_VERSION_FILE"


echo -e "$EXTENSION_NAME""DIRACOS $DIRACOS_EXT_VERSION $(date -u) based on DIRACOS $DIRACOS_VERSION\n\n" > $DIRACOS_EXT_VERSION_FILE

echo -e "===== Python packages ====\n\n" >> $DIRACOS_EXT_VERSION_FILE
# reminder: this file was generated when building the python modules
comm -3 before.txt after.txt | sed 's/\t//g' | sort >> $DIRACOS_EXT_VERSION_FILE

# Remove pyo and pyc
find $DIRACOS_PATH -name '*.py[oc]' -exec rm {} \;

# Fix the shebang
grep -rIl "\#\!$DIRACOS_PATH/usr/bin/python" $DIRACOS_PATH | xargs sed -i "s:\#\!$DIRACOS_PATH/usr/bin/python:\#\!/usr/bin/env python:g"


TAR_NAME="$EXTENSION_NAME"diracos-$DIRACOS_EXT_VERSION.tar.gz
# The hard-dereference options allow to replace a hard link with a copy of the file.
# A link pointing to nowhere would just be removed.
# We do not use the dereference option (for symlinks) because there are just too many
tar --hard-dereference -cvzf  $TAR_NAME diracos


tarRc=$?
# tar will probably return 1 because of --dereference and --hard-dereference (man tar is your friend)
# So I consider the tar a success if the returned code is 0 or 1
if [ $tarRc -eq 0 ] || [ $tarRc -eq 1 ];
then
  exit 0;
fi;
exit $tarRc
