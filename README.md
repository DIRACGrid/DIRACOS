# Principle

1. Create an empty repository
2. Compile our own python and make an RPM out of it in this repository
3. Rebuild all RPMs we need using this python
4. Extract all the RPMs and the dependencies
5. Install the python dependencies with pip
6. Bundle everything as a tarball


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

#  Building RPMs

The build of RPMs relies on mock (https://github.com/rpm-software-management/mock/wiki). This allows to build everything in an isolated environment.

The build is done starting from an SRPM package or from the fedora repo using fedpkg (https://pagure.io/fedpkg).


Once the rpms are built, they are copied to the repository you specify in your config files. The list of RPMs copied can be filtered.
Some RPMs can be required only for building purposes. When this is the case, these RPMs are not considered later on when creating the bundle.


## Patching the sources

It might be that you want to patch the spec file or even the source code. Either to not compile something useless, either because the SRPM is broken (bloody glite). This can be automated by puting a patch file in the patch directory specified in the configuration, and named `<package>.patch`.

The patch file should be generated:
* either using `git diff` in the case of fedpkg.
* or using `diff -u -r original patched`, where `original` is a folder containing the uncompressed SRPM before patching, and `patched` the same, but patched.

## Altering the normal build workflow

In case an RPM requires specific actions, these actions can be executed using `routines`. A routine is just a python file containing an `execute` method. All the configuration of the package is passed to this routine. There are three types of routines:
* pre-routine: executed before the normal workflow
* post-routine: executed after the normal workflow
* routine: executed instead of the normal workflow

The routine file has to be named `(post-|pre-)<package>.py`.

In case of a full routine, the routine is responsible for everything, from building to updating the repository.



# Python packages

The python packages are installed with pip inside a mock environment, using virtualenv. Running inside the mock environment ensures to use the lib packages needed from our repo.

# Creating the bundle

Once all the RPMs have been produced, we grab their dependencies and extract all this in a root. This looks like a complete filesystem root.
The python modules are then compiled and added to this tree.
The whole directory structure is tared.

## Bootstrap issue

There is a boostrap issue with mock: mock needs gdb which, when compiled with python support, needs python. The point is that we want to use pyton 2.7 (at the moment), which is different from the system python (2.6) used to compile gdb. Thus, to solve that, we need to:

1. Compile python and put it in our repository
2. Recompile gdb without python support, or with our python
3. Use this gdb instead of the system one.

## About EPEL repository

We could very well rely on the EPEL repository to provide most of the dependencies. The issue there is that it is very difficult to know if we are not rebuilding some of the dependencies of a given RPM, in which case one needs to recompile it as well.
In order to avoid such headache, we just exclude EPEL alltogether, and recompile it all.

# Generate a new diracos


The building procedure of a new diracos is completely automated. It requires that you have a few basic packages installed on your system, a few mock config files and a json file containing the list of packages you want. The grammar for this json file is described bellow.

## Initial setup

Tested from an SLC6 machine.

```
   # Install the few tools needed
   yum install -y mock rpm-build fedora-packager createrepo python-pip

   # Create the basic structure of your yum repository
   export DIRACOS_REPO=/diracos_repo
   mkdir -p $DIRACOS_REPO/i386 $DIRACOS_REPO/i686 $DIRACOS_REPO/src $DIRACOS_REPO/noarch $DIRACOS_REPO/x86_64 $DIRACOS_REPO/buildOnly
   createrepo $DIRACOS_REPO  

   # Install the diracos machinery (currently from github)
   #pip install diracos
   pip install git+https://github.com/DIRACGrid/DIRACOS.git

   # Get the configuration files by cloning the same repo
```



WARNING: the path of the repository is also writen in the mock configuration files as well as in the json file you use to build the packages

## Configuration files

You have to make sure that all the paths from the mock configuration files as well as the json configuration files are consistent.

For the mock configuration files, it is mostly the local repository that you have to check, it has to correspond to `DIRACOS_REPO`.

For the json file, the paths of mock have to match what is in the mock configuration files, and so does the repo. The paths for patches and routines can be relative, so it should work straight out of the checkout


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


```
dos-bundle /tmp/DIRACOS/config/lcgBundle.json
```

## Get your bundle


Copy it from your mock root in /tmp (e.g. /var/lib/mock/epel-6-x86_64-install/root/tmp/diracos-1.0.0.tar.gz)



# Adding a new package

## RPM package

Whether you want to replace an existing package by a newer version or add a completely new one, it is better to try first by hand. The process goes as follow:

1. Get your SRPM package
2. Patch it if needed
3. Build it

To build the SRPM package:

```
mock -r <mockConfigFile> --rebuild <SRPMFile>
```

If you want to patch it, you need to extract it, modify it, regenerate the SRPM from it


```
mkdir <workdir>
cd <workdir>
rpm2cpio <originaSRPMFile> | cpio -dvim
```

Modify the spec or the sources

```
mock -r <mockConfigFile> --buildsrpm --spec <specFile> --sources <workdir>
```

In case the SRPM contains only a spec file and an archive, the command becomes

```
mock -r <mockConfigFile> --buildsrpm --spec <specFile> --sources <tarFile>
```

Once you are happy with the result, just add the package the the json configuration file. If you modified the SRPM, you need to generate a patch file called `<package>.patch`, and put it in your patch directory.

```
diff -r -u <original> <patched>
```

where `<original>` contains the uncompressed original SRPM, and `<patched>` your modified version

# Configuration Grammar

The json formated files is used to describe what packages to build, as well as the environment in which to build it.


## rpmBuild section
This part of the configuration is used to build the RPMs. It is the `rpmBuild` attribute at the root of the json file.

The grammar is very flexible in the sense that no attribute is forbidden. The packages configuration is built by aggregating all the options as explained bellow, and each package is built in turn. There are however a few mandatory parameters.

### Package and PackageGroup

In order to simplify the configuration and make it more readable, the packages to build are organized in a sorted list (rpmBuild), grouped by "packageGroup". The complete package configuration will be the global configuration, on top of which we add the packageGroup configuration, on top of which we add the package specific configuration. For example:

```
{
   "rpmBuild" :
   {
     "opt1" : 1,
     "packageGroups" : [
         {
            "name" : "pkgGrp1",
            "opt1" : 2,
            "packages" : [
                {
                   "name" : "pkg1",
                   "opt2" : "x"
                },
                {
                   "name" : "pkg2",
                   "opt1" : 3
                }
            ]  
         }
     ]
  }
}
```

This will give the following packages:

```
{
   "name" : "pkg1",
   "opt1" : 2,
   "opt2" : "x"
}
{
   "name" : "pkg2",
   "opt1" : 3
}
```




#### Mandatory parameters


At the moment, there are no checks, but the program will crash.

* `mockConfig`: mock configuration file to use for the build
* `mockInstallConfig`: mock configuration file to use for the build of python module and packaging
* `mockRoot`: root directory where mock will work. WARNING: this value is related to the configuration in mockConfig.
* `mockInstallRoot`: root directory where mock will work. WARNING: this value is related to the configuration in mockConfig.
* `name`: The name of the package. Should be unique (CAUTION: no check on that yet). It is only used internaly.
* `packageGroups`: list of package groups. Must be there at the root of the json file.
* `packages`: each packageGroup should have a list of packages
* `patchDir`: directory where to look for the patches
* `pipBuildDependencies`: list of rpm packages required to perform the pip install
* `pipRequirements`: url to the requirements.txt file to feed pip
* `repo`: path to the repository where to copy the produced RPMs
* `routineDir`: directory where to look for routines
* `src`: The source of the package. Depending on what is passed here, the build procedure is slightly different. Currently, the src can either be the url of a SRPM, or the name of a fedora package.
* `version`: version of dirac os being built (just a tag...)



#### Optional parameters

* `branch`: usefull only when building fedpkg. This is the branch of the repo to build.
* `buildOnly`: boolean. if True, the RPMs are put in a different folder of the repository and are not considered for installation (unless required as dependency)
* `excludePatterns`: list of patterns against which the produced RPMs are matched. The RPMs matching any of these patterns are not copied to the repository. This is usefull to exclude for example doc or debuginfo RPMs straight after building them. Be careful that sometimes, the doc RPMs are required as dependencies...
* `pkgList`: list of RPMs to copy once the build is done. All the others are not copied.
* `workDir`: directory where the work will be done. Default to `/tmp`

Any other options will be read and passed to the build functions. Usefull examples can be "comment", or any other options your routines may need.



# Troubleshoot

## Build is failing for broken rpm dependencies

Sometimes, the build will fail, for some weird reasons. To start with, do not bother. Clean the mock cache, the mock work directory, and restart the build. It might just work

## Script fails for missing python module

When crashing, mock sometimes messes up the actual environment. Log out from the machine, come back, and try again.

## Issue with rpath

In the future, we might see issue with rpath

```
mock-chroot> sh-4.1# ldd /tmp/root/usr/lib64/python2.7/lib-dynload/pyexpat.so
	linux-vdso.so.1 =>  (0x00007fff6afac000)
	libexpat.so.1 => /tmp/root/lib64/libexpat.so.1 (0x00007fb9716ff000)
	libpython2.7.so.1.0 => /usr/lib64/libpython2.7.so.1.0 (0x00007fb971321000)
	libpthread.so.0 => /tmp/root/lib64/libpthread.so.0 (0x00007fb971104000)
	libc.so.6 => /tmp/root/lib64/libc.so.6 (0x00007fb970d70000)
	libdl.so.2 => /tmp/root/lib64/libdl.so.2 (0x00007fb970b6c000)
	libutil.so.1 => /tmp/root/lib64/libutil.so.1 (0x00007fb970969000)
	libm.so.6 => /tmp/root/lib64/libm.so.6 (0x00007fb9706e5000)
	/lib64/ld-linux-x86-64.so.2 (0x00007fb971b33000)

<mock-chroot> sh-4.1# readelf -d /tmp/root/usr/lib64/python2.7/lib-dynload/pyexpat.so  | grep RPAT
    0x000000000000000f (RPATH)              Library rpath: [/usr/lib64]
```

A tool can remove them if needed:
https://linux.die.net/man/1/chrpath

## CentOS7

Currently there is an issue with CentOS7.
The python scripts have `/usr/bin/env` as shebang. However, `/usr/bin/env` requires `GLIBC_2.14` on CentOS7, which is not in the `libc` shipped here. The solution is probably to fix the postinstall script of DIRAC to not use the system `env`

# Test DIRACOS

If you want to test DIRACOS, it is enough to do the following:

```
  https://raw.githubusercontent.com/DIRACGrid/DIRAC/integration/Core/scripts/dirac-install.py
  chmod +x dirac-install.py 
  ./dirac-install.py -r v6r20 --dirac-os --dirac-os-version=0.0.5 
```
If you want to install it together with your extension, you will most probably have to copy the diracos tar files from `http://lhcbproject.web.cern.ch/lhcbproject/dist/Dirac_project/installSource/` to your own baseURL

