#!/bin/bash
# This script is normally called automatically with the arguments taken from the json configuration file


# This is the file containing the loose requirements
# It was copied there by fixPipRequirementsVersions
PIP_REQUIREMENTS_LOOSE=/tmp/loose_requirements.txt

# This is the output files containing strict versions
PIP_REQUIREMENTS_FIXED=/tmp/fixed_requirements.txt


# the list of dependencies of to build the package
# and also fetch their dependency by pip-compile
PIP_BUILD_DEPENDENCIES="%(pipBuildDependencies)s"



echo "Installing pip"
cd /tmp
curl -O -L https://bootstrap.pypa.io/get-pip.py
python get-pip.py

echo "Installing pip-tools"
pip install pip-tools


# We need to install the dependencies such that pip-compile
# can work
echo "Pip build dependencies $PIP_BUILD_DEPENDENCIES"

echo "Installing dependency"
yum install -y $PIP_BUILD_DEPENDENCIES


echo "Fixing the version"


# First, get all the python packages which are not taken from git

grep -v 'git+' $PIP_REQUIREMENTS_LOOSE > $PIP_REQUIREMENTS_FIXED

# If there are packages from git, we can't compile them, so print a warning

gitPackages=$(grep 'git+https' $PIP_REQUIREMENTS_LOOSE)
# gitpackageFound is 0 if packages were found
gitPackagesRc=$?

if [ $gitPackagesRc -eq 0 ];
then
  echo "WARNING: cannot compile following packages"
  for pkg in $gitPackages;
  do
    echo $pkg;
  done;
fi


# Now, compile all the non packages
# The change is done in place
pip-compile -v $PIP_REQUIREMENTS_FIXED
compileRc=$?

if [ $compileRc -ne 0 ];
then
  echo "ERROR fixing version, exiting";
  exit 1;
fi

# add back the git packages

grep 'git+https' $PIP_REQUIREMENTS_LOOSE >> $PIP_REQUIREMENTS_FIXED


# # First, copy the git requirements to the target file
# grep 'git+' PIP_REQUIREMENTS_LOOSE > fixed_requirements.txt

# # Add the strict versions
# grep '==' PIP_REQUIREMENTS_LOOSE >> fixed_requirements.txt

# # Transform the '<=' requirements into '=='
# grep '<=' loose_requirements.txt | sed 's/<=/==/g' >> fixed_requirements.txt

# # For all the '>=', check the latest versions known to pip, and use that one
# for pkg in $(grep '>=' loose_requirements.txt | awk -F '[>=]' {'print $1'});
# do
#   # When asking pip to install version 0.0.0, it will fail and list you which available versions there are
#   latest=$(pip install $pkg==0.0.0 2>&1 | grep 'from versions' | awk -F '[,:]' {'print $NF'} | sed -e 's/)//g' -e 's/ //g');
#   echo "$pkg==$latest";
# done >> fixed_requirements.txt


# # For all the non specified version, check the latest versions known to pip, and use that one
# for pkg in $(grep -vE '(=|#|git)' loose_requirements.txt |  awk  {'print $1'});
# do
#   # When asking pip to install version 0.0.0, it will fail and list you which available versions there are
#   latest=$(pip install $pkg==0.0.0 2>&1 | grep 'from versions' | awk -F '[,:]' {'print $NF'} | sed -e 's/)//g' -e 's/ //g');
#   echo "$pkg==$latest";
# done >> fixed_requirements.txt
