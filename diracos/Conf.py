"""
Manages the configuration for diracos
"""

import json
import os


# Path that might be relative
PATH_OPTIONS = ("mockInstallConfig",
                "mockInstallRoot",
               )
PKG_PATH_OPTIONS = ("mockConfig",
                    "mockRoot",
                    "patchDir",
                    "routineDir",
                    "repo",
                    "workDir",
                   )


def load(jsonFile):
  """ Read a diracos configuration file.
      The rpmbuild configuration is factorized, and the relative paths are resolved.

      :param jsonFile: path to the json configuration file

      :returns: configuration dictionnary
  """

  confDirectory = os.path.dirname(jsonFile)

  with open(jsonFile) as fd:
    fullConf = json.load(fd)

    for opt in PATH_OPTIONS:
      if opt in fullConf:
        fullConf[opt] = os.path.abspath(os.path.join(confDirectory, fullConf[opt]))

    rpmBuildConf = fullConf['rpmBuild']

    allPackagesConfig = []

    # Start from the global config
    globalConfDict = {}

    packageGroupsConf = []

    # First read the simple configuration attributes
    for attr, val in rpmBuildConf.iteritems():
      if attr == 'packageGroups':
        packageGroupsConf = val
      else:
        globalConfDict[attr] = val

    # Then loop over every package group
    for pkgGrpConf in packageGroupsConf:
      packagesConf = []

      # Start the package group conf from the global one
      packageGroupConfDict = dict(globalConfDict)
      # First read the simple attributes
      for attr, val in pkgGrpConf.iteritems():
        if attr == 'packages':
          packagesConf = val
        else:
          packageGroupConfDict[attr] = val

      # Now loop on each package
      for pkgConf in packagesConf:
        packageConfDict = dict(packageGroupConfDict)
        packageConfDict.update(pkgConf)

        # Resolve relative path into absolute path
        for opt in PKG_PATH_OPTIONS:
          if opt in packageConfDict:
            # if it is one of the default mock config, it is not a path
            if opt == 'mockConfig' and os.path.splitext(packageConfDict[opt])[1] != '.cfg':
              continue

            packageConfDict[opt] = os.path.abspath(os.path.join(confDirectory, packageConfDict[opt]))

        allPackagesConfig.append(packageConfDict)

    fullConf['allPackagesConfig'] = allPackagesConfig

    return fullConf
