# Principle

The idea of DIRACOS is to rebuild all what we need from the system, and ship it all together as a big tarfile. The structure looks like a complete root filesystem.

1. Create an empty repository
2. Compile our own python and make an RPM out of it in this repository
3. Rebuild all RPMs we need using this python
4. Extract all the RPMs and the dependencies
5. Install the python dependencies with pip
6. Bundle everything as a tarball


## How it works

This process relies mostly on Fedora `mock` (https://github.com/rpm-software-management/mock/wiki) to build RPMs and to create isolated environment. Python packages are installed using pip.

### Bootstrap issue

There is a boostrap issue with mock: mock needs gdb which, when compiled with python support, needs python. The point is that we want to use python 2.7 (at the moment), which is different from the system python (2.6) used to compile gdb. Thus, to solve that, we need to:

1. Compile python and put it in our repository
2. Recompile gdb without python support, or with our python
3. Use this gdb instead of the system one.

### About EPEL repository

We could very well rely on the EPEL repository to provide most of the dependencies. The issue there is that it is very difficult to know if we are not rebuilding some of the dependencies of a given RPM, in which case one needs to recompile it as well.
In order to avoid such headache, we just exclude EPEL all together, and recompile it all.

### About links

Some RPMs or pip packages make use of links (symbolic or hard). Every symlink pointing outside of DIRACOS itself is removed by a copy, the others are left untouched. Hard links are always replaced by a copy, because some file system do not support them (in particular CVMFS, which will probably be the main mean of distribution)

### About dependencies

Once the list of RPM and python packages are built, we pull all their dependencies using the `yum` resolution mechanism. However we need a stop criteria. After a lot of testing, we decided that the best criteria was to stop whenever we see the `glibc` in the dependencies. Of course, there are other packages, from which we could pull deeper. But this did not give good results (too many useless things shipped), so we decided to add the `manualDependencies` functionality for such cases.

### Dynamic libraries

When dynamic libraries are resolved by `/lib64/ld-linux-x86-64.so.2` libraries are searched for using the following order:

1. The `RPATH` dynamic section of the ELF file
2. The `LD_LIBRARY_PATH` environment variable
3. The `RUNPATH` dynamic section of the ELF file
4. The default locations specified in the interpreter itself

Ordinarily the CentOS 6 SPRMs upon which DIRACOS is based find shared libraries by relying on the default locations (4).
As DIRACOS has to be relocatable this has to be overridden.
Prior to DIRACOS v1r10 this was achieved using the `LD_LIBRARY_PATH` environment variable however this interferes with the job payload in undesirable ways (see [DIRACGrid/DIRAC#4480](https://github.com/DIRACGrid/DIRAC/issues/4480)).
DIRACOS v1r10 uses `patchelf` to run a post processing step on the built binaries to modify the headers of all dynamically linked ELF files to add the `RPATH` section.
This is set to a path starting with `$ORIGIN/` to allow dependencies to be found relative to the current files location rather than using an absolute path.
This transformation is performed by `diracos/scriptTemplates/set_RPATH.py` which is called by `diracos/scriptTemplates/bundle_diracos_script_tpl.sh`.

## Supported platforms

Only SLC6 and CC7 are supported. We have automated tests for CentOS 8, LTS Ubuntu and Fedora, but if they fail, too bad ! Up to you to fix it if you wish

### Trick

If the tests are green, you can check gitlab-ci.yml to see what are the hooks we use to make the tests work on Fedora and Ubuntu. But again, use at your own risk, and do not ask for support.
