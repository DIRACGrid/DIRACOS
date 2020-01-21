""" This module contains the methods needed to bundle all the packages.
It is assumed that the repository exists and all the python module are compiled.
This code should in principle run inside the mock environment used to compile the python modules.
"""


import glob
import json
import logging
import os
import subprocess
from yum import rpmUtils


def _getPackageDependencies(packageSet, ignoredPackages=None):
  """ List the package on which a given set of package depends

      :param packageSet: iterable of packages from which we want the dependencies
      :param ignoredPackages: set of packages to always ignore

  """

  if not ignoredPackages:
    ignoredPackages = set()

  repoQueryCmd = [
      'repoquery',
      '--queryformat',
      '"%{name}"',
      '--requires',
      '--resolve',
      '--pkgnarrow=all'] + list(packageSet)

  logging.debug("Getting dependencies using %s", repoQueryCmd)
  deps = set([p for p in subprocess.check_output(
      repoQueryCmd).replace('"', '').split('\n') if p]) - ignoredPackages
  return deps


def _unrollPackageDependencies(requiredPackages, ignoredPackages=None):
  """ Starting from one or several package, get the dependencies
      recursively until we reach glibc.

      Note that this stopping criteria may lead to a premature stop, since
      other packages at the same level as glibc in the dependency chain
      could be pulled futher.
      But experience shows that this is the best stopping criteria if
      we do not want to ship a whole distribution.

      :param requiredPackages: iterable of packages
      :param ignoredPackages: set of packages to always ignore


      :return: set of packages
  """

  oldPackages = set()
  newPackages = requiredPackages

  while newPackages:
    oldPackages.update(newPackages)
    if 'glibc' in newPackages:
      logging.debug('Stopping here')
      break
    newPackagesDep = _getPackageDependencies(newPackages, ignoredPackages=ignoredPackages)

    newPackages = newPackagesDep - oldPackages
    logging.debug("Old packages %s", len(oldPackages))
    logging.debug("New packages %s", len(newPackages))

  return oldPackages


def _getPackagesURLs(packages):
  """
      Given a list of packages, return the urls at which we can get them

      :param packages: iterable of package names

      :return: list of URLs
  """

  yumdownloaderCmd = ['yumdownloader', '-x', '*i686', '--urls', '--downloadonly'] + list(packages)
  logging.debug("Getting list of package urls using %s", yumdownloaderCmd)
  return [url for url in subprocess.check_output(yumdownloaderCmd).split('\n') if url]


def _resolveAllPackageDependencyURLs(requiredPkg=None, ignoredPackages=None):
  """
      Given a list of package, get a complete list of dependencies (modulo a bit of filtering),
      and resolve their URL.

      :param requiredPkg: packages that we are interested in bundeling. If not specified, relies on
                          the repository and will take all the packages under x86_64 and noarch
      :param ignoredPackages: set of packages to always ignore
      :param pkgListFile: if specified, dump in this path the list of packages required
      :param requiredByFile: if specified, dump in this path the mapping of which packages are requiring a given package
      :param onlyForDepFile: if specified, dump in this path the list of packages pulled only for dependencies
  """

  pkgListFile = '/tmp/pkgList.txt'
  requiredByFile = '/tmp/requiredBy.txt'
  onlyForDepFile = '/tmp/onlyForDep.txt'

  # Just for information purposes. Keep the info of which package is required by which one
  requiredBy = {}
  logging.info("Resolving the dependencies for %s", requiredPkg)

  pkgs = set()
  # Unroll each package.
  # We do not do them all at once, because we would stop at the first one that
  # requires glibc...
  for pkg in requiredPkg:
    if pkg in ignoredPackages:
      logging.debug("Skipping %s as it is in ignoredPackages", pkg)
      continue
    upkg = _unrollPackageDependencies([pkg], ignoredPackages=ignoredPackages)
    logging.debug("%s requires %s", pkg, upkg)

    # update the requiredBy dict.
    [requiredBy.setdefault(p, []).append(pkg) for p in upkg]
    # Include the new required packages
    pkgs.update(upkg)

  logging.debug("Removing glibc from the package list")
  try:
    pkgs.remove('glibc')
  except Exception as e:
    logging.debug("EXCEPTION %s", e)

  if pkgListFile:
    with open(pkgListFile, 'w') as fd:
      fd.write("%s" % '\n'.join(sorted(pkgs)))

  if onlyForDepFile:
    with open(onlyForDepFile, 'w') as fd:
      fd.write("%s" % '\n'.join((pkgs - requiredPkg)))

  if requiredByFile:
    with open(requiredByFile, 'w') as fd:
      for x, y in requiredBy.iteritems():
        fd.write("%s:%s\n" % (x, sorted(y)))

  return _getPackagesURLs(pkgs)


def _doBundleDIRACOS(
        diracOsVersion,
        requiredPkg=None,
        repository=None,
        ignoredPackages=None,
        removedFolders=None,
        manualDependencies=None):
  """
      Create the final diracos tarball.

    :param diracOsVersion: just a tag to name the diracos archive
    :param requiredPkg: packages that we are interested in bundeling. If not specified, relies on
                        the repository and will take all the packages under x86_64 and noarch
    :param repository: path to the repository
    :param ignoredPackages: set of packages to always ignore
    :param removedFolders: list of folders in DIRACOS we can remove at the end of the build
    :param manualDependencies: set of dependencies that we have to manually add.
                              See the doc for details about this feature.

  """

  logging.info("Bundleing DIRACOS version %s", diracOsVersion)

  if not requiredPkg:
    # Take the RPMs from x86_64 and noarch
    dirToExplore = [os.path.join(repository, subdir) for subdir in ('x86_64', 'noarch')]
    allRPMs = [
        os.path.basename(rpm) for subDir in dirToExplore for rpm in glob.glob(
            '%s/*.rpm' %
            subDir)]

    # Take the package name, only if it is not a doc and debuginfo
    requiredPkg = set([rpmUtils.miscutils.splitFilename(rpm)[0]
                       for rpm in allRPMs if '-doc-' not in rpm and 'debuginfo' not in rpm])

  # Adding the list of packages that needs to pulled manually
  requiredPkg = requiredPkg.union(manualDependencies)

  urlList = _resolveAllPackageDependencyURLs(requiredPkg=requiredPkg,
                                             ignoredPackages=ignoredPackages)

  # urlList = [ 'file:///diracos_repo//x86_64/globus-gss-assist-10.15-1.el6.py27.usc4.x86_64.rpm']
  logging.debug("urlList %s", urlList)

  # Write the list of rpms to a file /tmp/rpms.txt
  # It is meant to be kept in the tar for info
  # We do not keep the whole URL, just the package name
  rpmVersionsFile = '/tmp/rpms.txt'
  with open(rpmVersionsFile, 'w') as rvf:
    for pkgUrl in urlList:
      rvf.write('%s\n' % os.path.basename(pkgUrl))

  if not removedFolders:
    removedFolders = ['aStupidRandomNameToAvoidDeletingSomethingUseful']

  # At this point in time, we are in the mock environment. So the template shell script
  # will not be anymore where BUNDLE_DIRACOS_SCRIPT_SH_TPL_PATH points,
  # but in /tmp/, because that's where diracoslib.py put it before
  # Also, we have no access to the BUNDLE_DIRACOS_SCRIPT_SH_TPL_PATH variable anymore anyway

  bundleTpmPath = '/tmp/bundle_diracos_script_tpl.sh'

  with open(bundleTpmPath, 'r') as tplFile:
    bundle_diracos_script_tpl = ''.join(tplFile.readlines())

  shellBundleScript = '/tmp/bundleDiracOS.sh'
  with open(shellBundleScript, 'w') as sbs:
    sbs.write(
        bundle_diracos_script_tpl % {
            'diracOsVersion': diracOsVersion,
            'requiredPackages': ' '.join(urlList),
            'removedFolders': ' '.join(removedFolders)})
  os.chmod(shellBundleScript, 0o755)

  bundleCmd = ['/tmp/bundleDiracOS.sh']
  logging.debug("building bundle with: %s", bundleCmd)

  subprocess.check_call(bundleCmd)


def main():
  """ main method when started as a script  """
  logging.basicConfig(level=logging.DEBUG)

  jsonConf = '/tmp/conf.json'
  with open(jsonConf, 'r') as fd:
    cfg = json.load(fd)
    repository = cfg['rpmBuild']['repo']
    ignoredPkg = set(cfg['ignoredPackages'])
    diracOsVersion = cfg['version']
    removedFolders = cfg['removedFolders']
    manualDependencies = set(cfg['manualDependencies'])

  _doBundleDIRACOS(
      diracOsVersion,
      repository=repository,
      ignoredPackages=ignoredPkg,
      removedFolders=removedFolders,
      manualDependencies=manualDependencies)


if __name__ == '__main__':
  # If we call this as a script, it means we are inside the mock
  # environment, so we can assume fix paths
  main()
