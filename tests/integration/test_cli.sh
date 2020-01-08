#!/bin/bash

# This script is used to test the binaries
# It just calls them with the --help flag,
# or -h, or without. Any of these should be working
# otherwise we consider it an issue

scriptsToTest=(mysql gfal-ls gfal-stat myproxy-info voms-proxy-init2 rrdtool);
rc=0

for script in "${scriptsToTest[@]}"; do
   # Try --help first
   if ! ${script} --help &>/dev/null; then
     # Try just -h
     if ! ${script} -h &>/dev/null; then
      # If it still fails, try with no options
       if ! ${script}  &>/dev/null; then
         # If it still fails, it fails...
         rc=1;
       fi
     fi
   fi
done

# Now some specific tests that do not behave like the other binaries

# For BDDI and ARC
if ! (ldapsearch --help 2>&1 >/dev/null | grep -q "usage: ldapsearch"); then
  echo "ldapsearch not working";
  rc=1;
fi

# For SSHComputingElement
if ! (ssh --help 2>&1 >/dev/null | grep -q "usage:"); then
  echo "ssh not working";
  rc=1;
fi

# For https://github.com/DIRACGrid/DIRACOS/issues/107
if ! (git --exec-path | grep "${DIRAC}"); then
  echo "git --exec-path does not contain ${DIRAC}";
  rc=1;
fi

exit $rc
