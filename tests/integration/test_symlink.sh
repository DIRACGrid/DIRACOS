#!/bin/bash

# This script ensures that there are no symlink in DIRACOS pointing outside of it
# it assumes that the DIRACOS environment variable is defined.

# This line finds all the symlinks, look at where they point, and makes sure
# there's no absolute path, for example:
# ./usr/lib64/python2.7/os.py -> /usr/lib64/python2.7/os.py

# We also replace path starting with $DIRACOS to './'

find $DIRACOS -type l -exec ls -l {} \; | sed "s|-> $DIRACOS|-> ./|g" | grep '\-> /'

# If grep returns 0, some items were found -> not good
if [ $? -eq 0 ];
then
   echo "Some absolute symlinks were found";
   exit 1;
else
   echo "No absolute symlink found, all good."
   exit 0;
fi
