#!/usr/bin/env python
import sys
import json
from diracos import Conf, diracoslib
import logging
import pprint


def main():
  logging.basicConfig(level=logging.DEBUG)
  jsonConf = sys.argv[1]

  cfg = Conf.load(jsonConf)

  mockInstallConfig = cfg.get('mockInstallConfig')
  mockInstallRoot = cfg.get('mockInstallRoot')
  pipRequirements = cfg['pipRequirements']
  pipBuildDependencies = cfg.get('pipBuildDependencies')

  # No need to do it in mock if there are no build dependencies
  fixedVersionFile = diracoslib.fixPipRequirementsVersions(
      mockInstallConfig, mockInstallRoot, pipRequirements, pipBuildDependencies)
  print "Fixed version file in %s" % fixedVersionFile


if __name__ == '__main__':
  main()
