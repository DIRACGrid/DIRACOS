#!/usr/bin/env python
import sys
sys.path.append('/root/DIRACOS')

import json
from diracos import Conf, diracoslib
import logging
logging.basicConfig(level=logging.DEBUG)

import pprint


def main():
  jsonConf = sys.argv[1]

  cfg = Conf.load(jsonConf)
  diracoslib.bundleDIRACOS(cfg)


if __name__ == '__main__':
  main()
