""" Test the configuration of diracos"""
import os

from context import diracos
from diracos import Conf


from pytest import mark
parametrize = mark.parametrize

testDir = os.path.join(os.path.dirname(__file__), 'testFiles')


def test_get_all_packages():
  """ Check that we get all the packages in the correct order
      and with correct inheritance
  """
  json_test_file = os.path.join(os.path.dirname(__file__), 'testFiles/config_test.json')
  cfg = Conf.load(json_test_file)
  allPackages = cfg['allPackagesConfig']

  # Most paths should be relative now !

  assert len(allPackages) == 4

  pkg1 = allPackages[0]
  assert pkg1['name'] == 'grp1_pkg1_name'

  assert pkg1['mockRoot'] == os.path.join(testDir, 'grp1_pkg1_mockRoot')

  pkg2 = allPackages[1]
  assert pkg2['name'] == 'grp1_pkg2_name'
  assert pkg2['mockRoot'] == os.path.join(testDir, 'grp1_mockRoot')

  pkg3 = allPackages[2]
  assert pkg3['name'] == 'grp2_pkg1_name'
  assert pkg3['mockRoot'] == os.path.join(testDir, 'grp2_pkg1_mockRoot')

  pkg4 = allPackages[3]
  assert pkg4['name'] == 'grp2_pkg2_name'
  assert pkg4['mockRoot'] == os.path.join(testDir, 'mockRoot')


def test_resolve_mockConfig():
  """ mockConfig should resolved to an absolute path, except if it is a standard config"""

  json_test_file = os.path.join(os.path.dirname(__file__), 'testFiles/config_test.json')
  cfg = Conf.load(json_test_file)
  allPackages = cfg['allPackagesConfig']

  # If the mockConfig is a '.cfg' path, it should be resolved to an absolute path
  pkg1 = allPackages[0]
  assert pkg1['mockConfig'] == os.path.join(testDir, 'grp1_pkg1_mockConfig.cfg')

  # If not, it should stay as it is
  pkg2 = allPackages[2]
  assert pkg2['mockConfig'] == 'grp2_pkg1_mockConfig'


pipRequirementsTests = [
    # URL case
    (os.path.join(
        testDir,
        'pip_req_url.json'),
        "https://aURL.com/requirements.txt"),
    # path case
    (os.path.join(
        testDir,
        'pip_req_file.json'),
     os.path.abspath(os.path.join(
         testDir,
         "../requirements.txt")))]


@parametrize("cfgFile,pipReqExpected", pipRequirementsTests)
def test_resolve_requirement(cfgFile, pipReqExpected):
  """pipRequirement can be a url or a path
     If we have an URL, it should stay as is
     If it is a path, we want it to be resolved to absolute path
  """

  cfg = Conf.load(cfgFile)
  requirementURL = cfg['pipRequirements']
  assert requirementURL == pipReqExpected
