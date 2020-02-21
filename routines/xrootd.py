import logging
import shutil
import subprocess
from diracos import diracoslib
import os
import glob
import tarfile
from yum import rpmUtils

# TODO: factorize with glite-ce-cream-cli.py, since it is essentialy the same thing


def _mock_patchAndRecreateGlite(srpmFile, patchFile, mockConfigFile=None, mockRoot=None):
  """ Patch and recreate an SRPM """

  tmpDir = diracoslib._extractSRPM(srpmFile)
  tarFn = os.path.join(tmpDir, "xrootd.tar.gz")
  # extract the archive as well
  tar = tarfile.open(tarFn, "r:gz")
  filesToCompress = tar.getnames()
  tar.extractall(path=tmpDir)
  tar.close()

  diracoslib._applyPatch(patchFile, tmpDir)

  # retar the file
  os.unlink(tarFn)
  tar = tarfile.open(tarFn, "w:gz")
  for fn in filesToCompress:
    tar.add(os.path.join(tmpDir, fn), arcname=fn)
  tar.close()

  specFile = glob.glob(os.path.join(tmpDir, '*.spec'))[0]
  sources = glob.glob(os.path.join(tmpDir, '*.tar.gz'))[0]
  diracoslib._mockBuildSRPM(specFile, sources, mockConfigFile)
  newSrcRpm = diracoslib._copyRPMs(os.path.join(mockRoot, 'result/'), tmpDir)[0]
  return newSrcRpm


def execute(**kwargs):
  """ This requires also patching the tar.gz"""

  logging.info("Executing xrootd routine")
  logging.debug("Arguments %s", kwargs)

  SRPMFile = kwargs['src']
  repository = kwargs['repo']
  mockConfig = kwargs['mockConfig']
  mockRoot = kwargs['mockRoot']
  patchDir = kwargs['patchDir']
  patchFile = None

  logging.info("Building %s %s", SRPMFile, "%s" % ("with mockConfig %s" % mockConfig
                                                   if mockConfig else ""))

  if not os.path.isfile(SRPMFile):
    logging.debug("SRPM file is an URL, download it first")
    SRPMFile = diracoslib._downloadFile(SRPMFile, '/tmp')

  # get package name
  pkgName, pkgVersion, _release, _epoch, _arch = rpmUtils.miscutils.splitFilename(
      os.path.basename(SRPMFile))

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
    newSRPM = _mock_patchAndRecreateGlite(SRPMFile, patchFile, mockConfig, mockRoot=mockRoot)
    logging.debug("New SRPM file %s", newSRPM)
    SRPMFile = newSRPM

  diracoslib._mockRebuild(SRPMFile, mockConfig)
  mockResultDir = os.path.join(mockRoot, 'result/')
  diracoslib._copyRPMs(mockResultDir, repository, byRPMType=True)
  diracoslib._createRepo(repository)
  logging.info('Finished')
