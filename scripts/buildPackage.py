#!/usr/bin/env python
import sys

import json
from diracos import Conf,diracoslib
import logging
logging.basicConfig(level=logging.DEBUG)

import pprint

def main():
  jsonConf = sys.argv[1]
  pkgName = sys.argv[2]
  cfg = Conf.load(jsonConf)
  allPackages = cfg['allPackagesConfig']
  #pprint.pprint(allPackages)

  for package in allPackages:
    if package.get('name') == pkgName:
      diracoslib.buildPackage(package)



if __name__ == '__main__':
  main()
