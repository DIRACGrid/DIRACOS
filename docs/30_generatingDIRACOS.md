# Generate a new diracos


The building procedure of a new diracos is completely automated. It requires that you have a few basic packages installed on your system, a few mock config files and a json file containing the list of packages you want. The grammar for this json file is described bellow.

It must be run from an SLC6 machine (or container).


CAUTION: if inside Docker, special care must be taken (https://github.com/rpm-software-management/mock/wiki#mock-inside-docker)
```
  docker run --privileged --cap-add=SYS_ADMIN -it cern/slc6-base bash
```

Carefull, some compilations are a bit violent, so disabling oom killer can be needed by adding to docker run :
```
--oom-kill-disable=true
```

Also you need to make sure that your containers have enough free space (20G). Consider adding the following to the dockerd sysconfig file. However, note that it will impact ALL your containers

```
--storage-opt dm.basesize=20G'
```

## Initial setup

```
   # Install the few tools needed
   yum install -y mock rpm-build fedora-packager createrepo python-pip

   # Create the basic structure of your yum repository
   export DIRACOS_REPO=/diracos_repo
   mkdir -p $DIRACOS_REPO/i386 $DIRACOS_REPO/i686 $DIRACOS_REPO/src $DIRACOS_REPO/noarch $DIRACOS_REPO/x86_64 $DIRACOS_REPO/bootstrap $DIRACOS_REPO/buildOnly

   # Needed for speedup optimization
   curl -o $DIRACOS_REPO/bootstrap/lbzip2-2.5-2.el6.x86_64.rpm -L http://lhcb-rpm.web.cern.ch/lhcb-rpm/dirac/DIRACOS/bootstrap/lbzip2-2.5-2.el6.x86_64.rpm
   curl -o $DIRACOS_REPO/bootstrap/pigz-2.3.4-1.el6.x86_64.rpm -L http://lhcb-rpm.web.cern.ch/lhcb-rpm/dirac/DIRACOS/bootstrap/pigz-2.3.4-1.el6.x86_64.rpm

   createrepo $DIRACOS_REPO  

   # Install the diracos machinery (currently from github)
   #pip install diracos
   pip install git+https://github.com/DIRACGrid/DIRACOS.git

   # Get the configuration files by cloning the same repo
   git clone https://github.com/DIRACGrid/DIRACOS.git

   # if you are building a specific tag, don't forget to check it out
   # git checkout XYZ
```



WARNING: the path of the repository is also writen in the mock configuration files as well as in the json file you use to build the packages

## Configuration files

You have to make sure that all the paths from the mock configuration files as well as the json configuration files are consistent.

For the mock configuration files, it is mostly the local repository that you have to check, it has to correspond to `DIRACOS_REPO`.

For the json file, the paths of mock have to match what is in the mock configuration files, and so does the repo. The paths for patches and routines can be relative, so it should work straight out of the checkout

These are all the places where the `DIRACOS_REPO` is referred:

  * https://github.com/DIRACGrid/DIRACOS/blob/master/mockConfigs/mock-build-diracos.cfg#L93
  * https://github.com/DIRACGrid/DIRACOS/blob/master/mockConfigs/mock-install-diracos.cfg#L9
  * https://github.com/DIRACGrid/DIRACOS/blob/master/mockConfigs/mock-install-diracos.cfg#L94
  * https://github.com/DIRACGrid/DIRACOS/blob/master/config/diracos.json#L9

 If you do not change the above mentioned lines, you have to have `$DIRACOS_REPO=/diracos_repo`, otherwise the compilation will fail.

 Finally, you can optimize the build by specifying the number of processors you want to use in the mock config file https://github.com/DIRACGrid/DIRACOS/blob/master/mockConfigs/mock-build-diracos.cfg#L9


## Building everything


First you build all the RPMs:

```
dos-build-all-rpms <jsonFile>
```

For example
```
dos-build-all-rpms /tmp/DIRACOS/config/diracos.json
```

if you want to build a single Package

```
dos-build-package <jsonFile> <packageName>
```

## Build the python modules

Currently, there is a different mock file. It is basically the same but mount a few folder inside the chroot. Maybe eventually I can merge them in a single one.

The following script

```
dos-build-python-modules <jsonFile>
```
## Bundle DIRACOS

Just packages eveything in a single tar file:

```
dos-bundle <jsonFile>
```

For example

```
dos-bundle /tmp/DIRACOS/config/diracos.json
```

## Get your bundle


Copy it from your mock root in /tmp (e.g. /var/lib/mock/epel-6-x86_64-install/root/tmp/diracos-1.0.0.tar.gz)

## Test it !

You can run this in any machine (tested on SLC6 & CC7), not necessarily the one from which you built.

The current test consist in a python files that will try to import pretty much all the python modules used in DIRAC, and make sure they are taken from diracos directory.

The test files (`test_sumlink.sh`, `knowBrokenLinks.txt` and `testImports.py`) are in the repository that you checked out for the config, under tests/integrations.


```
   # go in a temporary directory, and untar DIRACOS

   cd /tmp
   untar diracos-1.0.0.tar.gz

   # Enter a new shell (so in case of problem, you just logout)
   bash

   # Setup the DIRACOS environment variable
   export DIRACOS=/tmp/diracos

   # setup the environment (more or less how DIRAC will do)
   source $DIRACOS/diracosrc

   # run the test
   pytest test_import.py
   test_symlink.sh
   # exit the shell
   exit
```
