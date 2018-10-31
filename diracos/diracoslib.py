""" Basic building blocks to build DIRACOS """

import glob
import imp
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from yum import rpmUtils


def _downloadFile(url, dest):
  """
      Just downloads a file.

      :param url: source url or file
      :param dest: directory or destination path

      :returns: the path to the downloaded file
  """

  logging.debug('Beginning file download: %s', url)

  if os.path.isdir(dest):
    dest = os.path.join(dest, os.path.basename(url))

  logging.debug("Writing to %s", dest)

  # This downloading does not work because some sites
  # moved their repository to TLS, and there is no way
  # in python 2.6 to configure the SSL context.
  # That's why we have to use a system command..
  # with open(dest, 'wb') as df:
  #  df.write(urllib.urlopen(url).read())

  dl_cmd = ['curl', '-o', dest, '-L', url]
  logging.debug("Downloading with %s", ' '.join(dl_cmd))
  subprocess.check_call(dl_cmd)

  return dest


def _extractSRPM(srpmFile, workDir=None):
  """
     Uncompress an srpm.

     The work is done in a temporary directory.
     The SRPM is moved into this temporary directory

     :param srpmFile: srpm file to decompress

     :returns: path to the temp directory

  """
  logging.debug("Extracting SRPM %s", srpmFile)
  # Create a temporary directory to work in
  tmpDir = tempfile.mkdtemp(dir=workDir)
  logging.debug("Working in %s", tmpDir)

  # move the srpm there
  shutil.move(srpmFile, tmpDir)

  newSrpmFile = os.path.join(tmpDir, os.path.basename(srpmFile))
  tmpCPIOArchive = os.path.join(tmpDir, 'archive.cpio')

  # First extract the cpio archive from the srpm
  rpm2cpioCmd = ['/usr/bin/rpm2cpio', newSrpmFile]
  logging.debug("Extracting cpio archive from srpm: %s", rpm2cpioCmd)

  with open(tmpCPIOArchive, 'wb') as cpioArch:
    subprocess.check_call(rpm2cpioCmd, stdout=cpioArch)

  # Now extract the content of the cpio archive
  # IDIOTIC CPIO !!!! default slc6 version does not know -D option
  # so I have to change current directory.
  curDir = os.getcwd()
  try:
    os.chdir(tmpDir)
    cpioCmd = ['cpio', '-dvim']
    logging.debug("Extracting content of cpio:%s", cpioCmd)
    with open(tmpCPIOArchive, 'rb') as cpioArch:
      subprocess.check_call(cpioCmd, stdin=cpioArch)
  finally:  # always go back, no matter what
    os.chdir(curDir)

  # Remove the intermediate files
  os.remove(tmpCPIOArchive)
  os.remove(newSrpmFile)

  return tmpDir


def _applyPatch(patchFile, dirPath):
  """ Apply patch.
      It is assumed that the diff was done on a directory with the uniform option.
      (diff -u -r original/ patched/)

      :param patchFile: path to the patchFile
      :param dirPath: path to the directory to patch

      :returns: None
  """
  logging.debug("Patching %s with %s", dirPath, patchFile)

  patchCmd = ['/usr/bin/patch', '-d', dirPath, '-i', patchFile, '-p1']
  logging.debug("Patch command: %s", patchCmd)
  subprocess.check_call(patchCmd)


def _applyGitPatch(patchFile, dirPath):
  """ Apply a Git patch.
      It is assumed that the diff was done using git diff.

      :param patchFile: path to the patchFile
      :param dirPath: path to the git directory


      :returns: None
  """
  logging.debug("Patching %s with %s", dirPath, patchFile)

  patchCmd = ['/usr/bin/git', 'apply', '--directory', dirPath, patchFile]
  logging.debug("Patch command: %s", patchCmd)
  subprocess.check_call(patchCmd)


def _mockBuildSRPM(specFile, sources, mockConfigFile=None):
  """ Build an srpm from the spec file and the sources

      :param specFile: path to the spec file
      :param sources: path to the source archive
      :param mockConfigFile: path to the mock config file

  """

  cmd = ['/usr/bin/mock']
  if mockConfigFile:
    cmd += ['-r', mockConfigFile]
  cmd += ['--buildsrpm', '--spec', specFile, '--sources', sources]

  logging.debug("Generating SRPM with %s", cmd)
  subprocess.check_call(cmd)


def _mock_patchAndRecreateSRPM(srpmFile, patchFile, mockConfigFile, mockRoot, workDir=None):
  """ Patch and recreate an SRPM using mock.

      The work is done in a temporary dir.

      :param srpmFile: path to the srpm file
      :param patchFile: path to the patch file
      :param mockConfigFile: mock config file to use (path or name)
      :param mockRoot: path of mock builts

      :returns: path to the newly created SRPM

  """

  tmpDir = _extractSRPM(srpmFile, workDir=workDir)
  _applyPatch(patchFile, tmpDir)

  specFile = glob.glob(os.path.join(tmpDir, '*.spec'))[0]

  # Now there are two cases when rebuilding:
  # * either the original src.rpm had spec file + sources in tar
  #    -> pass the tar file to mock as sources
  # * or it has many more files.
  #    -> pass the directory to mock as sources

  if len(os.listdir(tmpDir)) > 2:  # spec + tar
    sources = tmpDir
  else:
    sources = glob.glob(os.path.join(tmpDir, '*.tar.gz'))[0]

  # Build the SRPM and put it in our temp directory
  # (otherwise it is wiped out when building it...)
  _mockBuildSRPM(specFile, sources, mockConfigFile)
  newSrcRpm = _copyRPMs(os.path.join(mockRoot, 'result/'), tmpDir)[0]

  return newSrcRpm


def _buildFromFedpkg(packageCfg):
  """
      Build a package using fedpkg.
      It requires the package name and the branch.
      It will checkout the package, patch it (if needed),
      build the SRPMs, build the RPMs and add them to the repo.

      :param packageCfg: full package configuration
  """

  pkgName = packageCfg['src']
  repository = packageCfg['repo']
  branch = packageCfg['branch']
  mockConfig = packageCfg['mockConfig']
  mockRoot = packageCfg['mockRoot']
  patchDir = packageCfg['patchDir']
  patchFile = packageCfg.get('patchFile')
  buildOnly = packageCfg.get('buildOnly', False)
  workDir = packageCfg.get('workDir', '/tmp')
  excludePatterns = packageCfg.get('excludePatterns')
  pkgList = packageCfg.get('pkgList')

  logging.info("Building %s from fedpkg branch %s", pkgName, branch)
  tmpDir = tempfile.mkdtemp(dir=workDir)
  logging.debug("Working in %s", tmpDir)
  fedPkgClone = ['fedpkg', '--path', tmpDir, 'clone', '--anonymous', pkgName]
  logging.debug("Getting fedpkg with %s", fedPkgClone)
  subprocess.check_call(fedPkgClone)

  # Append the pkgName to the tmp directory
  tmpDir = os.path.join(tmpDir, pkgName)

  fedPkgSRPM = ['fedpkg', '--path', tmpDir, 'switch-branch', branch]
  logging.debug("Changing branch %s", fedPkgSRPM)
  subprocess.check_call(fedPkgSRPM)

  if not patchFile and patchDir:

    potentialPatchFile = os.path.join(patchDir, '%s.patch' % pkgName)
    logging.debug("Checking existance of %s", potentialPatchFile)
    if os.path.isfile(potentialPatchFile):
      logging.debug("patch file found")
      patchFile = potentialPatchFile

  if patchFile:
    _applyGitPatch(patchFile, tmpDir)

  fedPkgSRPM = ['fedpkg', '--path', tmpDir, 'srpm']
  logging.debug("Generating fedpkg srpm %s", fedPkgSRPM)
  subprocess.check_call(fedPkgSRPM)

  # Find the source SRPM generated
  srpmFile = glob.glob('%s/*.src.rpm' % tmpDir)[0]

  # If the src.rpm is already in the repo, do not rebuild it
  # here we do not check the pkgRelease because it will be the fedora name (i.e. f24)
  # while the one we end up having in our repo is our custom one (el6.py27 for example)
  _pkgName, pkgVersion, _pkgRelease, _epoch, _arch = rpmUtils.miscutils.splitFilename(
      os.path.basename(srpmFile))
  existingBuild = glob.glob(
      os.path.join(
          repository, '*/%s-%s*src.rpm' %
          (pkgName, pkgVersion)))

  if existingBuild:
    logging.info("The repo already contains a build, not rebuilding: %s", existingBuild)
    return

  _mockRebuild(srpmFile, mockConfig)
  mockResultDir = os.path.join(mockRoot, 'result/')

  rpmDestDir = repository
  byRPMType = True
  # We only build, so we copy the rpms to a special directory
  if buildOnly:
    rpmDestDir = os.path.join(rpmDestDir, 'buildOnly')
    byRPMType = False

  _copyRPMs(
      mockResultDir,
      rpmDestDir,
      byRPMType=byRPMType,
      excludePatterns=excludePatterns,
      pkgList=pkgList)
  _createRepo(repository)
  logging.info('Finished')


def _buildFromSRPM(packageCfg):
  """
      Build a package starting from an SRPM.
      It will download the file if needed, patch it (if needed),
      build the RPMs, and add them to the repo.

      :param packageCfg: full package configuration

  """

  # Get the configuration needed

  srpmFile = packageCfg['src']
  repository = packageCfg['repo']
  mockConfig = packageCfg['mockConfig']
  mockRoot = packageCfg['mockRoot']
  patchDir = packageCfg['patchDir']
  patchFile = None
  buildOnly = packageCfg.get('buildOnly', False)
  workDir = packageCfg.get('workDir', '/tmp')
  excludePatterns = packageCfg.get('excludePatterns')
  pkgList = packageCfg.get('pkgList')

  logging.info("Building %s %s", srpmFile, "%s" % ("with mockConfig %s" % mockConfig
                                                   if mockConfig else ""))

  # get package name
  pkgName, pkgVersion, pkgRelease, _epoch, _arch = rpmUtils.miscutils.splitFilename(
      os.path.basename(srpmFile))

  # If the src.rpm is already in the repo, do not rebuild it

  existingBuild = glob.glob(
      os.path.join(
          repository, '*/%s-%s-%s*src.rpm' %
          (pkgName, pkgVersion, pkgRelease)))
  if existingBuild:
    logging.info("The repo already contains a build, not rebuilding: %s", existingBuild)
    return

  # if the file is not available locally, download it
  if not os.path.isfile(srpmFile):
    logging.debug("SRPM file is an URL, download it first")
    srpmFile = _downloadFile(srpmFile, workDir)

  # If no patchFile is specified but we have a patchDir,
  # try to find a patch file called like the package
  if not patchFile and patchDir:

    potentialPatchFile = os.path.join(patchDir, '%s.patch' % pkgName)
    logging.debug("Checking existance of %s", potentialPatchFile)
    if os.path.isfile(potentialPatchFile):
      logging.debug("patch file found")
      patchFile = potentialPatchFile

  # We have a patch file ? Well, use it !
  if patchFile:
    newSRPM = _mock_patchAndRecreateSRPM(srpmFile, patchFile, mockConfig, mockRoot=mockRoot)
    logging.debug("New SRPM file %s", newSRPM)
    srpmFile = newSRPM

  # Now we have an srpm package like we want it.
  # So we build it, and add the produced RPMs in
  # our repository

  _mockRebuild(srpmFile, mockConfig)
  mockResultDir = os.path.join(mockRoot, 'result/')

  rpmDestDir = repository
  byRPMType = True
  # We only build, so we copy the rpms to a special directory
  if buildOnly:
    rpmDestDir = os.path.join(rpmDestDir, 'buildOnly')
    byRPMType = False

  _copyRPMs(
      mockResultDir,
      rpmDestDir,
      byRPMType=byRPMType,
      excludePatterns=excludePatterns,
      pkgList=pkgList)
  _createRepo(repository)
  logging.info('Finished')


def _mockRebuild(srpmFile, mockConfigFile):
  """
       Rebuild RPMs from a SRPM using mock

       :param srpmFile: path to the SRPM file
       :param mockConfigFile: path to the mock config file. Otherwise, mock will use the system one
  """

  cmd = ['/usr/bin/mock']
  if mockConfigFile:
    cmd += ['-r', mockConfigFile]
  cmd += ['--rebuild', srpmFile]

  logging.debug("Rebuild SRPM with %s", cmd)
  subprocess.check_call(cmd)


def _createRepo(repository, initRepo=False):
  """
      Call createrpo on the repository

      :param repository: path to the repository
      :param initRep: if True, intialize the repo from scratch
  """

  cmd = ['/usr/bin/createrepo']
  if not initRepo:
    cmd.append('--update')
  cmd.append(repository)

  logging.debug("Creating repo with %s", cmd)

  subprocess.call(cmd)


def _copyRPMs(srcDir, destDir, byRPMType=False, excludePatterns=None, pkgList=None):
  """ Copy all the rpms in a directory to a destination

      :param srcDir: path to the source directory
      :param destDir: destination directory (normally a repo...)
      :param byRPMType: if True, look at the architecture of the RPM and put it in a subdir
  """

  # Do not take the src rpm, we keep it for later
  rpmList = filter(lambda rpm: 'src.rpm' not in rpm, glob.glob(os.path.join(srcDir, '*.rpm')))
  logging.debug("RPM files found: %s", rpmList)

  # Put the SRPM aside so that it is not taken instead of the binary rpm
  # when looking for a specific list of packages
  srpmFile = glob.glob(os.path.join(srcDir, '*src.rpm'))[0]
  logging.debug("SRPM file found: %s", srpmFile)

  # If we have a specific list of packages
  if pkgList:
    logging.debug("Looking for specific packages %s", pkgList)
    # Create a dict <package name, rpm path>
    rpmPathDict = dict(
        (rpmUtils.miscutils.splitFilename(
            os.path.basename(rpm))[0],
            rpm) for rpm in rpmList)
    logging.debug("Found following packages %s", rpmPathDict)
    rpmList = [rpmPathDict[pkg] for pkg in pkgList]
  # If we have some exclusion pattern
  elif excludePatterns:
    logging.debug("Filtering list with pattern %s", excludePatterns)
    rpmList = [rpm for rpm in rpmList if not any([re.match(p, rpm) for p in excludePatterns])]

  # put back the srpm
  rpmList.append(srpmFile)

  logging.debug("RPM files to copy: %s", rpmList)
  copiedRpms = []
  for rpm in rpmList:
    finalDest = destDir
    if byRPMType:
      finalDest = os.path.join(destDir, rpmUtils.miscutils.splitFilename(os.path.basename(rpm))[-1])
    shutil.copy2(rpm, finalDest)
    copiedRpms.append(os.path.join(destDir, os.path.basename(rpm)))
  return copiedRpms


def _executeRoutine(routineFile, **kwargs):
  """ Execute a routine and passes it whatever argument is passed here

      The routine is imported as a module, and we call the execute function.

      :param routineFile: path to the routine

  """
  routineModule = imp.load_source('diracosroutine', routineFile)
  routineModule.execute(**kwargs)


def buildPackage(packageCfg):
  """ Build a package from its configuration.
      This is the entry point for any build.

      It will try to infer what sort of package is being built (using the src field).
      It will also take care of invocking the various routines that
      might be defined (preRoutine, postRoutine or routine).

      :param packageCfg: complete package build configuration

  """

  src = packageCfg['src']

  routineDir = packageCfg.get('routineDir', '')
  routineFile = os.path.join(routineDir, '%s.py' % packageCfg['name'])
  preRoutineFile = os.path.join(routineDir, 'pre-%s.py' % packageCfg['name'])

  # if a routine is defined, run it, and next
  if os.path.exists(routineFile):
    logging.debug("ROUTINE FILE %s", routineFile)
    _executeRoutine(routineFile, **packageCfg)
  else:

    #preRoutine = packageCfg.get('preRoutine')
    if os.path.exists(preRoutineFile):
      # run preRoutine
      _executeRoutine(preRoutineFile, **packageCfg)

    _root, srcExtension = os.path.splitext(src)

    if srcExtension == '.rpm':  # In fact, it is .src.rpm
      _buildFromSRPM(packageCfg)
    elif srcExtension == '':  # fedpkg
      _buildFromFedpkg(packageCfg)
    else:
      raise ValueError("No clue what to do with %s" % src)

    postRoutine = packageCfg.get('postRoutine')
    if postRoutine:
      routineFile = os.path.join(packageCfg['routineDir'], 'post-%s.py' % packageCfg['name'])
      _executeRoutine(routineFile, **packageCfg)



# This is the template file used to generate the shell script to build the python modules
BUILD_PYTHON_MODULE_SH_TPL = """#!/bin/bash
# This script is normally called automatically with the arguments taken from the json configuration file

PIP_BUILD_DEPENDENCIES="%(pipBuildDependencies)s"
PIP_DIRAC=/tmp/pipDirac

echo "Installing pip"
cd /tmp
curl -O -L https://bootstrap.pypa.io/get-pip.py
python get-pip.py

echo "Preparing to build pythong packages"

echo "Pip build dependencies $PIP_BUILD_DEPENDENCIES"

echo "Installing dependency"
yum install $PIP_BUILD_DEPENDENCIES

yum install python2-virtualenv

# We use the --always-copy option in order not to have
# symlinks to the system.
# However, we cannot just do virtualenv --always-copy /tmp/pipDirac
# See: https://github.com/pypa/virtualenv/issues/565#issuecomment-305002914

mkdir $PIP_DIRAC
cd $PIP_DIRAC
virtualenv .
cd /tmp/

source $PIP_DIRAC/bin/activate
pip install -r /tmp/requirements.txt
virtualenv --relocatable $PIP_DIRAC
"""


def buildPythonModules(
        mockInstallConfig,
        mockInstallRoot,
        pipRequirementFile,
        pipBuildDependencies):
  """
      Make a pip install of all the requirements in pipRequirementFile inside a
      mock environemnt, using virtualenv.
      The RPM dependencies listed in pipBuildDependencies are installed before.

      :warn: for the moment, it is expected that this whole DIRACOS repository is available under /root
      in the mock environemnt. This is achieved by mounting the directory in the mockInstallConfig file.

      :param mockInstallConf: path to the mock config file in which to perform the build
      :param mockInstallRoot: root path of the mock installation
      :param pipRequirementFile: url/path to the requirements.txt
      :param pipBuildDependencies: list of RPM packages to install prior to building.

  """

  # First, init the environment

  mockInitCmd = ['mock', '-r', mockInstallConfig, '--init']
  logging.debug("Initializing environment with: %s", mockInitCmd)

  subprocess.check_call(mockInitCmd)

  # We need to put the requirments.txt in the mock directory.
  # if it is a file, we copy it, if not, we download it
  # The destination is always /tmp/requirements.txt
  pipRequirementInMock = os.path.join(mockInstallRoot, 'root/tmp/requirements.txt')
  if os.path.isfile(pipRequirementFile):
    shutil.copy(pipRequirementFile, pipRequirementInMock)
  else:
    _downloadFile(pipRequirementFile, pipRequirementInMock)

  shellBuildScript = os.path.join(mockInstallRoot, 'root/tmp/buildPythonModules.sh')
  with open(shellBuildScript, 'w') as sbs:
    sbs.write(
        BUILD_PYTHON_MODULE_SH_TPL % {
            'pipBuildDependencies': ' '.join(pipBuildDependencies)})
  os.chmod(shellBuildScript, 0o755)

  logging.info("Building python modules")
  logging.debug("mockInstallConfig %s", mockInstallConfig)
  logging.debug("pipRequirementFile %s", pipRequirementFile)
  logging.debug("pipBuildDependencies %s", pipBuildDependencies)

  #shellArgs = ' '.join(['root/tmp/buildPythonModules.sh', pipRequirementFile] + pipBuildDependencies)

  pipBuildCmd = ['mock', '-r', mockInstallConfig, '--shell', '/tmp/buildPythonModules.sh']
  logging.debug("building python packages with: %s", pipBuildCmd)

  subprocess.check_call(pipBuildCmd)


def bundleDIRACOS(fullCfg):
  """
      Create the final diracos tarball.

      This method is in fact just a bootstrap.
      It copies the configuration and a few python files inside the mock environment, so they can be used
      in isolation.



    :param fullCfg: full configuration loaded

  """

  logging.info("Bootstraping packaging of diracos")

  # We copy the bundlelib and the json conf in the mock environment and run that

  mockInstallRoot = fullCfg['mockInstallRoot']
  mockInstallConfig = fullCfg['mockInstallConfig']

  jsonConfPath = os.path.join(mockInstallRoot, 'root/tmp/conf.json')
  bundlelibDestPath = os.path.join(mockInstallRoot, 'root/tmp/bundlelib.py')
  bundlelibSrcPath = os.path.join(os.path.dirname(__file__), 'bundlelib.py')

  shutil.copyfile(bundlelibSrcPath, bundlelibDestPath)
  os.chmod(bundlelibDestPath, 0o755)

  with open(jsonConfPath, 'w') as jc:
    json.dump(fullCfg, jc)

  bundleCmd = ['mock', '-r', mockInstallConfig, '--shell', 'python /tmp/bundlelib.py']
  subprocess.check_call(bundleCmd)


FIX_PIP_REQUIREMENTS_VERSIONS_SH_TPL = """#!/bin/bash
# This script is normally called automatically with the arguments taken from the json configuration file


# This is the file containing the loose requirements
# It was copied there by fixPipRequirementsVersions
PIP_REQUIREMENTS_LOOSE=/tmp/loose_requirements.txt

echo "Installing pip"
cd /tmp
curl -O -L https://bootstrap.pypa.io/get-pip.py
python get-pip.py

echo "Fixing the version"

# First, copy the git requirements to the target file
grep 'git+' loose_requirements.txt > fixed_requirements.txt

# Add the strict versions
grep '==' loose_requirements.txt >> fixed_requirements.txt

# Transform the '<=' requirements into '=='
grep '<=' loose_requirements.txt | sed 's/<=/==/g' >> fixed_requirements.txt

# For all the '>=', check the latest versions known to pip, and use that one
for pkg in $(grep '>=' loose_requirements.txt | awk -F '[>=]' {'print $1'});
do
  # When asking pip to install version 0.0.0, it will fail and list you which available versions there are
  latest=$(pip install $pkg==0.0.0 2>&1 | grep 'from versions' | awk -F '[,:]' {'print $NF'} | sed -e 's/)//g' -e 's/ //g');
  echo "$pkg==$latest";
done >> fixed_requirements.txt


# For all the non specified version, check the latest versions known to pip, and use that one
for pkg in $(grep -vE '(=|#|git)' loose_requirements.txt |  awk  {'print $1'});
do
  # When asking pip to install version 0.0.0, it will fail and list you which available versions there are
  latest=$(pip install $pkg==0.0.0 2>&1 | grep 'from versions' | awk -F '[,:]' {'print $NF'} | sed -e 's/)//g' -e 's/ //g');
  echo "$pkg==$latest";
done >> fixed_requirements.txt

"""


def fixPipRequirementsVersions(mockInstallConfig,
                               mockInstallRoot,
                               pipRequirementFile):
  """
      Takes a pip requirements file, and prints it with fixed versions.
      The versions are tacken from the mock environent

      * packages from git are left untouched
      * requirements '==' are left untouched
      * requirements '<=' are fixed to '=='
      * requirements '>=' are fixed to the latest version available
      * requirements with no version are fixed to the latest available

      :param mockInstallConf: path to the mock config file in which to perform the build
      :param mockInstallRoot: root path of the mock installation
      :param pipRequirementFile: url/path to the requirements.txt

      :returns: path to the requirements file with fixed versions
  """



  # First, init the environment

  mockInitCmd = ['mock', '-r', mockInstallConfig, '--init']
  logging.debug("Initializing environment with: %s", mockInitCmd)

  subprocess.check_call(mockInitCmd)

  logging.info("Fixing versions of requirements file")

  # We need to put the requirments.txt in the mock directory.
  # if it is a file, we copy it, if not, we download it
  # The destination is always /tmp/loose_requirements.txt
  pipRequirementInMock = os.path.join(mockInstallRoot, 'root/tmp/loose_requirements.txt')
  if os.path.isfile(pipRequirementFile):
    shutil.copy(pipRequirementFile, pipRequirementInMock)
  else:
    _downloadFile(pipRequirementFile, pipRequirementInMock)

  # We copy the script to fix the versions in the mock environment

  shellFixVersionsScript = os.path.join(mockInstallRoot, 'root/tmp/fixPipVersions.sh')
  with open(shellFixVersionsScript, 'w') as sbs:
    sbs.write(FIX_PIP_REQUIREMENTS_VERSIONS_SH_TPL)
  os.chmod(shellFixVersionsScript, 0o755)

  fixVersionsCmd = ['mock', '-r', mockInstallConfig, '--shell', '/tmp/fixPipVersions.sh']
  subprocess.check_call(fixVersionsCmd)

  return os.path.join(mockInstallRoot, 'root/tmp/fixed_requirements.txt')
