import logging
import shutil
import subprocess

def execute(**kwargs):
  logging.info("Executing post GDB routine")
  logging.debug("Arguments %s",kwargs)
  logging.debug("Removing gdb from mock")
  subprocess.check_call(['mock', '--remove', 'gdb'])
  logging.debug("Cleaning mock cache")
  mockRoot = kwargs['mockRoot']
  mockCache = mockRoot.replace('/lib/', '/cache/')
  shutil.rmtree(mockCache)
  logging.info("GDB routine executed")
