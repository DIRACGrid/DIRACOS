import logging
import shutil

def execute(**kwargs):
  logging.info("Executing pre globus-gridftp-server routine")
  logging.debug("Arguments %s",kwargs)
  logging.debug("Cleaning mock cache and root")
  mockRoot = kwargs['mockRoot']
  mockCache = mockRoot.replace('/lib/', '/cache/')
  try:
    shutil.rmtree(mockCache)
  except Exception as e:
    logging.warn("Error removing Cache %s",e)
  try:
    shutil.rmtree(mockRoot)
  except Exception as e:
    logging.warn("Error removing mock Root %s",e)

  logging.info("globus-gridftp-server routine executed")
