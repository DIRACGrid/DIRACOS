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

There is a boostrap issue with mock: mock needs gdb which, when compiled with python support, needs python. The point is that we want to use pyton 2.7 (at the moment), which is different from the system python (2.6) used to compile gdb. Thus, to solve that, we need to:

1. Compile python and put it in our repository
2. Recompile gdb without python support, or with our python
3. Use this gdb instead of the system one.

### About EPEL repository

We could very well rely on the EPEL repository to provide most of the dependencies. The issue there is that it is very difficult to know if we are not rebuilding some of the dependencies of a given RPM, in which case one needs to recompile it as well.
In order to avoid such headache, we just exclude EPEL alltogether, and recompile it all.
