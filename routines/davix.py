import logging
import shutil
import subprocess
from diracos import diracoslib
import os
import glob
import tarfile
import tempfile
from yum import rpmUtils

# TODO: factorize with glite-ce-cream-cli.py, since it is essentialy the same thing

# Original URL:  https://github.com/Kitware/CMake/releases/download/v3.19.3/cmake-3.19.3-Linux-x86_64.sh
CMAKE3_SLC6_INSTALLER = 'https://diracos.web.cern.ch/diracos/bootstrap/cmake-3.19.3-Linux-x86_64.sh'


def execute(**kwargs):
  """ This requires also patching the tar.gz"""

  logging.info("Executing xrootd routine")
  logging.debug("Arguments %s", kwargs)

  srpmFile = kwargs['src']
  repository = kwargs['repo']
  mockConfig = kwargs['mockConfig']
  mockRoot = kwargs['mockRoot']
  patchDir = kwargs['patchDir']
  patchFile = None

  workDir = kwargs.get('workDir', '/tmp')

  logging.info("Building %s %s", srpmFile, "%s" % ("with mockConfig %s" % mockConfig
                                                   if mockConfig else ""))

  if not os.path.isfile(srpmFile):
    logging.debug("SRPM file is an URL, download it first")
    srpmFile = diracoslib._downloadFile(srpmFile, '/tmp')

  # get package name
  pkgName, pkgVersion, _release, _epoch, _arch = rpmUtils.miscutils.splitFilename(
      os.path.basename(srpmFile))

  # If the src.rpm is already in the repo, do not rebuild it
  #
  existingBuild = glob.glob(os.path.join(repository, 'src', '%s-%s*' % (pkgName, pkgVersion)))
  if existingBuild:
    logging.info("The repo already contains a build, not rebuilding: %s", existingBuild)
    return

  if not patchFile and patchDir:

    potentialPatchFile = os.path.join(patchDir, '%s.patch' % pkgName)
    logging.debug("Checking existance of %s", potentialPatchFile)
    if os.path.isfile(potentialPatchFile):
      logging.debug("patch file found")
      patchFile = potentialPatchFile

  if patchFile:
    newSRPM = diracoslib._mock_patchAndRecreateSRPM(srpmFile, patchFile, mockConfig, mockRoot=mockRoot)
    logging.debug("New SRPM file %s", newSRPM)
    srpmFile = newSRPM

  # now comes the funky part !
  # Davix decided to use cmake3, which is not easily available on SLC6 as RPM.
  # Luckily for us, there is a binary distribution by cmake themselves which works fine.
  # So we just extract it in the mock environment,
  # and build the RPM without cleaning !

  installer = diracoslib._downloadFile(CMAKE3_SLC6_INSTALLER, workDir)

  mockUsrDir = os.path.join(mockRoot, 'root/usr/')
  cmd = ['sh', installer, '--skip-license', '--prefix=%s' % mockUsrDir]
  logging.info("Installing cmake3 in the mock environment %s", cmd)
  subprocess.check_call(cmd)

  diracoslib._mockRebuild(srpmFile, mockConfig, noClean=True)
  mockResultDir = os.path.join(mockRoot, 'result/')
  diracoslib._copyRPMs(mockResultDir, repository, byRPMType=True)
  diracoslib._createRepo(repository)
  logging.info('Finished')
