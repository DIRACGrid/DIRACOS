#!/usr/bin/env python
import sys
import json
from diracos import Conf
import logging
logging.basicConfig(level=logging.DEBUG)

import pprint

def main():
  jsonConf = sys.argv[1]
  cfg = Conf.load(jsonConf)
  pprint.pprint(cfg)

if __name__ == '__main__':
  main()
