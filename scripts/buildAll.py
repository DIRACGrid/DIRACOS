#!/usr/bin/env python
import logging
import pprint
import sys

from diracos import Conf, diracoslib

logging.basicConfig(level=logging.DEBUG)


def main():
  jsonConf = sys.argv[1]
  cfg = Conf.load(jsonConf)
  allPackages = cfg['allPackagesConfig']
  pprint.pprint(allPackages)

  totalPackages = len(allPackages)
  for packageId, package in enumerate(allPackages, 1):
    logging.info("Building %s (%s/%s)", package['name'], packageId, totalPackages)
    diracoslib.buildPackage(package)


if __name__ == '__main__':
  main()
