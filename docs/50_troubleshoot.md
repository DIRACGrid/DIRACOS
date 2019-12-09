# Troubleshoot

## Error `Requires: python(abi) = 2.6`

If you see such an error, start by comparing the version of the complaining package with the one which is in the diracos_repo. If they do not match, then you need to update the version shipped with DIRACOS.


The whole point of building so many RPMs is because we try to get ride of python2.6 in all the low level packages. If you see such a message, that means that one of the package you are building requires a dependency that we do not provide. And if that's the case, you might want to look at version change. For example::

```
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
 ```

 This stack trace is due to `rpm-python-4.8.0-59` being pulled from the `base` repo, despite we provide `rpm-python-4.8.0-55`. This is because some packages (`yum` in that case) has a loose dependency (no specific version ) on `rpm-python`, so it takes the latest. The solution is to update our version of `rpm-python`



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

## Symlinks

Some RPMs will create broken symlinks. The existing ones are know, and are in the file `tests/integration/knownBrokenLinks.txt`. Shall a new one appear, this test should trigger, and you should either fix it, or add it to the list.

## Singularity

Singularity needs to be built from source to disable `setuid` support and make the binaries smaller by stripping debugging information.
It is tricky to build within DIRACOS due to it's dependency on `golang` as recent versions depend on `subversion` (for pulling dependencies).
As `subversion` has a lot of Python dependencies which it cause many errors of the form [`Requires: python(abi) = 2.6`](#error-requires-pythonabi--26) which eventually become circular dependencies when trying to rebuild everythin for Python 2.7.
Additionaly, compiling `golang` to remove the `subversion` dependency requires an existing `golang` package. Fortunately older `golang` pakcages don't require `subversion`, but does still require an existing `golang`.
This is avoided using prebuilt RPMs for an old `golang` version (split into `golang`/`golang-bin`/`golang-src`) that then enables a newer `golang` package to be built with the `subversion` dependency removed.
Singularity can then be built from source as is the case for other packages.
