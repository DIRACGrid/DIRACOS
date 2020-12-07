#!/bin/bash
# This script is normally called automatically with the arguments taken from the json configuration file
# If there are python packages to compile, the work will be done in the Mock environment
# Otherwise it will use Conda

# Exit directly in case of errors
set -e

# This is the file containing the loose requirements
# It was copied there by fixPipRequirementsVersions
PIP_REQUIREMENTS_LOOSE=/tmp/loose_requirements.txt

# This is the output files containing strict versions
PIP_REQUIREMENTS_FIXED=/tmp/fixed_requirements.txt


# the list of dependencies of to build the package
# and also fetch their dependency by pip-compile
PIP_BUILD_DEPENDENCIES="%(pipBuildDependencies)s"



if [ ! -z "$PIP_BUILD_DEPENDENCIES" ];
then
  echo "Installing pip"
  cd /tmp
  curl -O -L https://bootstrap.pypa.io/get-pip.py
  python get-pip.py pip==20.2.4

  echo "Installing pip-tools"
  pip install pip-tools


  # We need to install the dependencies such that pip-compile
  # can work
  echo "Pip build dependencies $PIP_BUILD_DEPENDENCIES"

  echo "Installing dependency"
  yum install -y $PIP_BUILD_DEPENDENCIES

else
  echo "No dependencies to be installed, using Conda"

  # The reason for using Conda is that we need pip-tools
  # which works only from python 2.7
  # but centos6 (which is the base for our build) has only 2.6
  cd /tmp/
  curl -O -L https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh
  chmod +x Miniconda2-latest-Linux-x86_64.sh
  ./Miniconda2-latest-Linux-x86_64.sh -b -p /tmp/condaFixVersions
  PATH=/tmp/condaFixVersions/bin:$PATH
  pip install pip-tools
fi

echo "Fixing the version"


# First, get all the python packages which are not taken from git

grep -v 'git+' $PIP_REQUIREMENTS_LOOSE > $PIP_REQUIREMENTS_FIXED

# If there are packages from git, we can't compile them, so print a warning

# We need to disable the 'exit on failure' feature because
# grep will return an error if not finding any git+https package
set +e

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

# Exit on failure again
set -e

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
set +e
grep 'git+https' $PIP_REQUIREMENTS_LOOSE >> $PIP_REQUIREMENTS_FIXED
set -e



if [ -z "$PIP_BUILD_DEPENDENCIES" ];
then
  echo "Removing conda"
  rm -rf /tmp/condaFixVersions
fi
