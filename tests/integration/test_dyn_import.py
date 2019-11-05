#!/usr/bin/env python
"""
Find the imports in a DIRAC checkout and make sure we can import them
"""

import os
import traceback
import warnings
import pytest
import sys
import findimports

parametrize = pytest.mark.parametrize

# The CLI equivalent to find the DIRAC imports is
# findimports -p --level=1 -T DIRAC/


# Use the environment variable to make it easy with pytest (it does not like cli arguments)
diracPath = os.environ['DIRAC']

# diracPath = '/home/chaen/dirac/DIRAC/DataManagementSystem/Client/'

# Find all the packages used by DIRAC
g = findimports.ModuleGraph()
g.parsePathname(diracPath)
# g.parsePathname('/tmp/cacheFile.importcache')
g = g.packageGraph(packagelevel=1).collapseTests()
moduleNames = set([i for m in g.listModules() for i in m.imports])

# some imports in DIRAC are fake, and are just for doc
# or formating example
# Ignore these
FAKE_MODULES = [
    'DIRAC',
    'more_local_stuff',
    'some_third_party_lib',
    'local_stuff',
    'some_third_party_other_lib',
    'dont_import_two',
    'modules_in_one_line']

moduleNames.difference_update(FAKE_MODULES)

# List here the modules that are allowed to Fail.
# Ideally, this should always be empty...
ALLOWED_TO_FAIL = ['cx_Oracle',  # This is used by some extensions and migration script (LFC->DFC),
                   'parameterized',  # testing
                   'diracdoctools',  # inside to DIRAC
                   'GitTokens',  # used for making releases
                   'PilotWrapper',  # in the pilot
                   'irods',  # not clear whether someone in DIRAC still uses it
                   'lfcthr',  # used by the LFC plugins
                   ]

# List of modules that need graphic libraries.
# When failing, these tests are just marked as skipped with a warning
GRAPHIC_MODULES = [
    'pylab',
]

diracosPath = os.environ['DIRACOS']


@parametrize('moduleName', moduleNames)
def test_module(moduleName):
  """ Try to import a module and check whether it is located in DIRACOS.

      Modules that are in the ALLOWED_TO_FAIL list are shown as skipped and generate a warning

      Modules that require graphic libraries on the system (GRAPHIC_MODULES) are skipped on container
  """

  try:
    module = __import__(moduleName)

    # Test whether it is correctly imported from DIRACOS

    try:
      modulePath = module.__file__
      # return true, if the common prefix of both is equal to directory
      # e.g. /a/b/c/d.rst and directory is /a/b, the common prefix is /a/b
      assert os.path.commonprefix([modulePath, diracosPath]) == diracosPath, \
          "ERROR %s not from DIRACOS: %s" % (moduleName, modulePath)

    # builtin modules like sys have no path
    except AttributeError as e:
      print "WARNING no path for %s" % moduleName

  except ImportError as e:
    msg = "could not import %s: %s" % (moduleName, repr(e))
    print traceback.print_exc()

    if moduleName in ALLOWED_TO_FAIL:
      warnings.warn(msg)
      pytest.skip("WARN: " + msg)
    elif moduleName in GRAPHIC_MODULES:
      warnings.warn(msg + "(Possibly due to system graphic libraries not present)")
      pytest.skip("WARN: " + msg + "(Possibly due to system graphic libraries not present)")
    else:
      pytest.fail("ERROR: " + msg)
