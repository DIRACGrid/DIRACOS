#!/bin/bash

# Exit directly in case of errors
set -e

# The list of PKGs we want to distribute.
# If not given as parameter, all the rpms in the x86_64 and noarch subfolder
# of the building repository will be used.
DIRACOS_VERSION=%(diracOsVersion)s
PKG_URLS="%(requiredPackages)s"
REMOVED_FOLDERS="%(removedFolders)s"

# Location where the bundle takes place
DIRACOS=/tmp/diracos
DIRACOSRC=$DIRACOS/diracosrc
DIRACOS_VERSION_FILE=$DIRACOS/versions.txt


echo "Extracting rpms $PKG_URLS"

mkdir $DIRACOS
cd $DIRACOS
for i in $PKG_URLS; do curl -L $i | rpm2cpio | cpio -dvim; done

# We need to copy the python modules using rsync
# because some directory are overwriten by files
yum install -y rsync

echo "Copying python modules"
rsync -zvr /tmp/pipDirac/lib/ $DIRACOS/usr/lib64/
cp -r /tmp/pipDirac/bin/ $DIRACOS/usr/

# Fix the shebang for python
echo "Fixing the shebang"
grep -rIl '#!/usr/bin/python' /tmp/diracos | xargs sed -i 's:#!/usr/bin/python:#!/usr/bin/env python:g'

# Generating the diracosrc
echo "Generating diracosrc $DIRACOSRC"

# add the list of rpms and python packages for info
echo "Adding the version list $DIRACOS_VERSION_FILE"


echo -e "DIRACOS $DIRACOS_VERSION $(date -u)\n\n" > $DIRACOS_VERSION_FILE
echo -e "===== RPM packages ====\n\n" >> $DIRACOS_VERSION_FILE
cat /tmp/rpms.txt | sort >> $DIRACOS_VERSION_FILE

echo -e "\n\n===== Python packages ====\n\n" >> $DIRACOS_VERSION_FILE
# reminder: this file was generated when building the python modules
cat /tmp/pythonPackages.txt | sort >> $DIRACOS_VERSION_FILE

# Doing some cleanup
echo "Removing useless folders"
for fold in $REMOVED_FOLDERS;
do
  echo "Removing $DIRACOS/$fold"
  rm -rf $DIRACOS/$fold;
done

# Remove pyo and pyc
find $DIRACOS -name '*.py[oc]' -exec rm {} \;

###############################################
# Here we just go through the symlinks, list
# the broken ones. We will compare them
# to a list of known broken links a posteriori
# The synlinks that points outside of diracos are
# replaced with a copy of the file
echo "Finding all the broken symlinks"

# Find all the symlinks
brokenLinks=$(
for i in $(find $DIRACOS -type l);
do
  # Find the target of the symlink
  fp=$(readlink $i);

  # If the target is an absolute path, but not in DIRACOS
  if [ $(echo $fp | sed "s|^$DIRACOS|./|g" | grep -cE '^/') -ne 0 ];
  then
    # If the target file does not exist, print a warning
    if [ ! -f $fp ];
    then
      # We display the link, but replace the actual DIRACOS path with just 'DIRACOS'
      echo -n "$i\n" | sed "s|^$DIRACOS|DIRACOS|g";
      # And we remove it
      rm $i;
    else
      # copy the original file
      cp --remove-destination $fp $i;
    fi;
  fi;
done)

echo "Found broken symlinks, put them in $DIRACOS/brokenLinks.txt"

# The file MUST be sorted for comparison, and we remove the empty lines
echo -e $brokenLinks | sort | sed '/^$/d' > $DIRACOS/brokenLinks.txt

###############################

cd /tmp
# The hard-dereference options allow to replace a hard link with a copy of the file.
# A link pointing to nowhere would just be removed.
# We do not use the dereference option (for symlinks) because there are just too many
tar --hard-dereference -cvzf diracos-$DIRACOS_VERSION.tar.gz diracos

tarRc=$?
# tar will probably return 1 because of --dereference and --hard-dereference (man tar is your friend)
# So I consider the tar a success if the returned code is 0 or 1
if [ $tarRc -eq 0 ] || [ $tarRc -eq 1 ];
then
  exit 0;
fi;
exit $tarRc
