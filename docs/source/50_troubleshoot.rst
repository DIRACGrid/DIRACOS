Troubleshoot
============

Error ``Requires: python(abi) = 2.6``
-------------------------------------

If you see such an error, start by comparing the version of the
complaining package with the one which is in the diracos_repo. If they
do not match, then you need to update the version shipped with DIRACOS.

The whole point of building so many RPMs is because we try to get rid
of python2.6 in all the low level packages. If you see such a message,
that means that one of the package you are building requires a
dependency that we do not provide. And if that’s the case, you might
want to look at version change. For example:

.. code-block:: text

   Getting requirements for yum-3.2.29-81.el6.py27.usc4.src
    --> python-2.7.13-2.el6.x86_64
    --> gettext-0.17-18.el6.x86_64
    --> intltool-0.41.0-1.1.el6.noarch
    --> python-nose-0.10.4-3.1.el6.py27.usc4.noarch
    --> python-2.7.13-2.el6.x86_64
    --> rpm-python-4.8.0-59.el6.x86_64
    --> Already installed : rpm-4.8.0-59.el6.x86_64
    --> python-iniparse-0.3.1-2.1.el6.py27.usc4.noarch
    --> python-2.7.13-2.el6.x86_64
    --> python-urlgrabber-3.9.1-11.el6.py27.usc4.noarch
    --> yum-metadata-parser-1.1.2-16.el6.py27.usc4.x86_64
    --> pygpgme-0.1-18.20090824bzr68.el6.py27.usc4.x86_64
   Error: Package: rpm-python-4.8.0-59.el6.x86_64 (base)
              Requires: libpython2.6.so.1.0()(64bit)
   Error: Package: rpm-python-4.8.0-59.el6.x86_64 (base)
              Requires: python(abi) = 2.6
              Installing: python-2.7.13-2.el6.x86_64 (local-py2.7)
                  python(abi) = 2.7
    You could try using --skip-broken to work around the problem
    You could try running: rpm -Va --nofiles --nodigest

This stack trace is due to ``rpm-python-4.8.0-59`` being pulled from the
``base`` repo, despite we provide ``rpm-python-4.8.0-55``. This is
because some packages (``yum`` in that case) has a loose dependency (no
specific version ) on ``rpm-python``, so it takes the latest. The
solution is to update our version of ``rpm-python``

Build is failing for broken rpm dependencies
--------------------------------------------

Sometimes, the build will fail, for some weird reasons. To start with,
do not bother. Clean the mock cache, the mock work directory, and
restart the build. It might just work

Script fails for missing python module
--------------------------------------

When crashing, mock sometimes messes up the actual environment. Log out
from the machine, come back, and try again.

Symlinks
--------

Some RPMs will create broken symlinks. The existing ones are know, and
are in the file ``tests/integration/knownBrokenLinks.txt``. Shall a new
one appear, this test should trigger, and you should either fix it, or
add it to the list.

Singularity
-----------

Singularity needs to be built from source to disable ``setuid`` support
and make the binaries smaller by stripping debugging information. It is
tricky to build within DIRACOS due to it’s dependency on ``golang`` as
recent versions depend on ``subversion`` (for pulling dependencies). As
``subversion`` has a lot of Python dependencies which it cause many
errors of the form
```Requires: python(abi) = 2.6`` <#error-requires-pythonabi--26>`__
which eventually become circular dependencies when trying to rebuild
everythin for Python 2.7. Additionaly, compiling ``golang`` to remove
the ``subversion`` dependency requires an existing ``golang`` package.
Fortunately older ``golang`` pakcages don’t require ``subversion``, but
does still require an existing ``golang``. This is avoided using
prebuilt RPMs for an old ``golang`` version (split into
``golang``/``golang-bin``/``golang-src``) that then enables a newer
``golang`` package to be built with the ``subversion`` dependency
removed. Singularity can then be built from source as is the case for
other packages.

About manualDependencies
------------------------

The packages that are in ``manualDependencies`` are added to the
dependencies that are pulled together with DIRACOS. In principle, since
we build all the packages we need and pull their dependencies, there
should be no need for such a thing. THere are however two cases where it
shows useful:

-  In case of RPM dependencies badly defined
-  In case of premature stop when pulling the dependencies.

``NSS`` falls in the later one.

LDD check failing
-----------------

The ``check_ldd`` test looks at the dependencies of the binaries in
DIRACOS. It finds those pointing outside of DIRACOS (can be due to
rpath) and those not found. There is a list of known “broken”
dependencies (``tests/integration/knownMissingDependencies.txt``).
Ideally, this list should be empty, but it will never be the case. So if
you cannot do differently, you can always add your libraries there.

ldconfig_scriptlets
-------------------

Some spec files use ``ldconfig_scriptlets`` to trigger ``ldconfig``.
This does not work with DIRACOS because it relies on some packages in
EPEL that we exclude on purpose. You can simply replace

::

   %ldconfig_scriptlets <A PACKAGE>

with

::

   %post <A PACKAGE> -p /sbin/ldconfig

   %postun <A PACKAGE> -p /sbin/ldconfig
