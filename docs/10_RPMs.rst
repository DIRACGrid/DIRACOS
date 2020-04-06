Building RPMs
=============

The build of RPMs relies on mock
(https://github.com/rpm-software-management/mock/wiki). This allows to
build everything in an isolated environment.

The build is done starting from an SRPM package or from the fedora repo
using fedpkg (https://pagure.io/fedpkg).

Once the rpms are built, they are copied to the repository you specify
in your config files. The list of RPMs copied can be filtered. Some RPMs
can be required only for building purposes. When this is the case, these
RPMs are not considered later on when creating the bundle.

It is very important to understand that the building procedure is
incremental. Packages are built in turn, and one package might likely
depend on its predecessor. So starting by trying to build the last
package from the list is bound to fail. This also means that if you are
changing a package in the middle, you might want to rebuild all what
comes after (so you might as well rebuild everything…).

A final note on the graphic libraries. They are just too big, too
complex, too plateform dependant to be shipped here. So it is assumed
that if you require X, you will install it independantely in your
system.

Patching the sources
--------------------

It might be that you want to patch the spec file or even the source
code. Either to not compile something useless, either because the SRPM
is broken (bloody glite). This can be automated by puting a patch file
in the patch directory specified in the configuration, and named
``<package>.patch``.

The patch file should be generated: \* either using ``git diff`` in the
case of fedpkg. \* or using ``diff -u -r original patched``, where
``original`` is a folder containing the uncompressed SRPM before
patching, and ``patched`` the same, but patched.

Altering the normal build workflow
----------------------------------

In case an RPM requires specific actions, these actions can be executed
using ``routines``. A routine is just a python file containing an
``execute`` method. All the configuration of the package is passed to
this routine. There are three types of routines: \* pre-routine:
executed before the normal workflow \* post-routine: executed after the
normal workflow \* routine: executed instead of the normal workflow

The routine file has to be named ``(post-|pre-)<package>.py``.

In case of a full routine, the routine is responsible for everything,
from building to updating the repository.

Caching mechanism
-----------------

In order to optimize the building mechanism, a caching mechanism is in
place, which avoids rebuilding a package that is already built. While
gaining speed, this might trick you as well by not rebuilding a package
that maybe requires to be. The mechanism is very simple: everytime a
package is built, the srpm is copied to the yum repository. When
building a package, if the corresponding SRPM with the correct version
is found in the yum repo, the built is skip. If you want to force a
rebuild, remove the srpm from the repository, and update it (not needed,
but cleaner).

Adding an RPM package
---------------------

Note: if you are adding a python module, use pip ! Not the RPM version.

Whether you want to replace an existing package by a newer version or
add a completely new one, it is better to try first by hand. The process
goes as follow:

1. Get your SRPM package
2. Patch it if needed
3. Build it

To build the SRPM package:

::

   mock -r <mockConfigFile> --rebuild <SRPMFile>

If you want to patch it, you need to extract it, modify it, regenerate
the SRPM from it

::

   mkdir <workdir>
   cd <workdir>
   rpm2cpio <originaSRPMFile> | cpio -dvim

Modify the spec or the sources

::

   mock -r <mockConfigFile> --buildsrpm --spec <specFile> --sources <workdir>

In case the SRPM contains only a spec file and an archive, the command
becomes

::

   mock -r <mockConfigFile> --buildsrpm --spec <specFile> --sources <tarFile>

Once you are happy with the result, just add the package the the json
configuration file. If you modified the SRPM, you need to generate a
patch file called ``<package>.patch``, and put it in your patch
directory.

If the package is meant to stay in DIRACOS, it should be uploaded to
DIRACOS srpm repository: https://diracos.web.cern.ch/diracos/SRPM/

::

   diff -r -u <original> <patched>

where ``<original>`` contains the uncompressed original SRPM, and
``<patched>`` your modified version

Common locations for packages include:

-  EPEL https://dl.fedoraproject.org/pub/epel/6/SRPMS/Packages/
-  Redhat
   http://ftp.redhat.com/pub/redhat/linux/enterprise/6Client/en/os/SRPMS/
   (and parent folder)
-  http://emisoft.web.cern.ch/emisoft/dist/EMI/3/sl6/SRPMS
-  http://dmc-repo.web.cern.ch/dmc-repo/el6/x86_64/

Note: For any middleware package, rather use the source repo (for
example http://dmc-repo.web.cern.ch/d) than derived (like EPEL)
