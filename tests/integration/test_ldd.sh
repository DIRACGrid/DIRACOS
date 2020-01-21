#!/bin/bash

# This script ensures that that the missing binary dependencies that were found during the build are
# all already known
# it assumes that the DIRACOS environment variable is defined.


# Return code
rc=0

###############################################
# Here we just go through the binaries, and
# check their dependencies. We will compare them
# to a list of known missing dependencies a posteriori
echo "Finding all the binary dependencies, and putting them in $DIRACOS/missingDependencies.txt"

# Find all the binaries
# check their dependencies
# remove those pointing inside DIRACOS
# keep only those pointing to an absolute path or not found

find $DIRACOS -type f -executable -exec ldd {} + | grep -v "$DIRACOS" | grep -E '(=> /|not found)' | awk {'print $1'} | sort -u > $DIRACOS/missingDependencies.txt

###############################

# We compare our list of missing dependencies with the known one (sort it before)
testDir=$(dirname $0)

newMissingDependencies=$(sort $testDir/knownMissingDependencies.txt | comm -13 - $DIRACOS/missingDependencies.txt );
if [ ! -z "$newMissingDependencies" ];
then
  echo "New missing dependencies"
  echo $newMissingDependencies;
  rc=1;
else
  echo "All OK";
fi


# Now check if some dependencies in the known lists have been unintentionaly resolved
resolvedDependencies=$(sort $testDir/knownMissingDependencies.txt | comm -23 - $DIRACOS/missingDependencies.txt );
if [ ! -z "$resolvedDependencies" ];
then
  echo "Some dependencies have been resolved"
  echo $resolvedDependencies;
  rc=1;
else
  echo "All OK";
fi



exit $rc;
