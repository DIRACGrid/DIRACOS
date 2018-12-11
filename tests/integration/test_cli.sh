#!/bin/bash

# This script is used to test the binaries
# It just calls them with the --help flag, 
# or -h, or without. Any of these should be working
# otherwise we consider it an issue

scriptsToTest=(mysql gfal-ls gfal-stat);
rc=0

for script in ${scriptsToTest[@]};
do
   # Try --help first
   ${script} --help &>/dev/null;
   if [ $? -ne 0 ];
   then
     # Try just -h
     ${script} -h &>/dev/null;
     # If it still fails, try with no options
     if [ $? -ne 0 ];
     then
       ${script}  &>/dev/null;
       # If it still fails, it fails...
       if [ $? -ne 0 ];
       then
         echo "$script seems not to be working"
         rc=1;
       fi
     fi
   fi
done

exit $rc

