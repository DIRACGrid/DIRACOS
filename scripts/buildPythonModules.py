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
  #pprint.pprint(allPackages)

  mockInstallConfig = cfg['mockInstallConfig']
  mockInstallRoot = cfg['mockInstallRoot']
  pipRequirements=  cfg['pipRequirements']
  pipBuildDependencies = cfg['pipBuildDependencies']


  diracoslib.buildPythonModules(mockInstallConfig, mockInstallRoot, pipRequirements, pipBuildDependencies)

if __name__ == '__main__':
  main()
