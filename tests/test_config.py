""" Test the configuration of diracos"""
import os

from context import diracos
from diracos import Conf
json_test_file = os.path.join(os.path.dirname(__file__), 'config_test.json')

cfg = Conf.load(json_test_file)

# def test_global_config_objects():
#   """ Checks that the configuration file is correctly read"""
#
#   for attr in ['mockConfig', 'mockRoot', 'patchDir', 'repo']:
#     assert getattr(cfg, attr) == attr
#
#   pkgGrp1 = cfg.packageGroups[0]
#   assert pkgGrp1.name == 'grp1'
#   for attr in ['mockConfig', 'mockRoot', 'patchDir', 'repo']:
#     assert getattr(pkgGrp1, attr) == 'grp1_%s'%attr
#
#   grp1Pkg1 = pkgGrp1.packages[0]
#   for attr in ['name', 'routine', 'src', 'mockConfig', 'mockRoot', 'patchDir', 'patchFile', 'repo']:
#     assert getattr(grp1Pkg1, attr) == 'grp1_pkg1_%s'%attr
#   for attr in ['buildOnly', 'disablePatch']:
#     assert getattr(grp1Pkg1, attr) is True
#
#   grp1Pkg2 = pkgGrp1.packages[1]
#   for attr in ['routine', 'mockConfig', 'mockRoot', 'patchDir', 'patchFile', 'repo']:
#     assert getattr(grp1Pkg2, attr) is None
#   for attr in ['name', 'src', ]:
#     assert getattr(grp1Pkg2, attr) == 'grp1_pkg2_%s'%attr
#   for attr in ['buildOnly', 'disablePatch']:
#     assert getattr(grp1Pkg2, attr) is False
#
#
#
#   # No specification in grp2, so it should all be None
#   pkgGrp2 = cfg.packageGroups[1]
#   assert pkgGrp2.name == 'grp2'
#   for attr in ['mockConfig', 'mockRoot', 'patchDir', 'repo']:
#     assert getattr(pkgGrp2, attr) is None
#
#   grp2Pkg1 = pkgGrp2.packages[0]
#   for attr in ['name', 'src', 'mockConfig', 'mockRoot', 'patchDir', 'patchFile']:
#     assert getattr(grp2Pkg1, attr) == 'grp2_pkg1_%s'%attr
#   for attr in ['routine', 'repo']:
#     assert getattr(grp2Pkg1, attr) is None
#   for attr in ['buildOnly', 'disablePatch']:
#     assert getattr(grp2Pkg1, attr) is True
#
#   grp2Pkg2 = pkgGrp2.packages[1]
#   for attr in ['routine', 'mockConfig', 'mockRoot', 'patchDir', 'patchFile', 'repo']:
#     assert getattr(grp2Pkg2, attr) is None
#   for attr in ['name', 'src', ]:
#     assert getattr(grp2Pkg2, attr) == 'grp2_pkg2_%s'%attr
#   for attr in ['buildOnly', 'disablePatch']:
#     assert getattr(grp2Pkg2, attr) is False

def test_get_all_packages():
  """ Check that we get all the packages in the correct order
      and with correct inheritance
  """
  allPackages = cfg['allPackagesConfig']

  assert len(allPackages) == 4

  pkg1 = allPackages[0]
  assert pkg1['name'] == 'grp1_pkg1_name'
  assert pkg1['mockRoot'] == 'grp1_pkg1_mockRoot'

  pkg2 = allPackages[1]
  assert pkg2['name'] == 'grp1_pkg2_name'
  assert pkg2['mockRoot'] == 'grp1_mockRoot'

  pkg3 = allPackages[2]
  assert pkg3['name'] == 'grp2_pkg1_name'
  assert pkg3['mockRoot'] == 'grp2_pkg1_mockRoot'

  pkg4 = allPackages[3]
  assert pkg4['name'] == 'grp2_pkg2_name'
  assert pkg4['mockRoot'] == 'mockRoot'
