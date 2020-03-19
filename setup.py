# This is the setup.py used to package the deployment script
# and fetch the needed dependecy

import os
from setuptools import setup, find_packages


base_dir = os.path.dirname(__file__)

# We want these 3 packages
packages = ['diracos', 'diracos.scripts', 'diracos.tests']

# We have to manually place scripts and tests under diracos package
# as they physically are not in the subdirectory
# https://docs.python.org/2/distutils/setupscript.html#listing-whole-packages
package_dir = {'diracos': os.path.join(base_dir, 'diracos'),
               'diracos.scripts': os.path.join(base_dir, 'scripts'),
               'diracos.tests': os.path.join(base_dir, 'tests')
               }

setup(
    name='diracos',
    description='Tools to build DIRACOS',
    version="1.0.0",
    author='Christophe Haen',
    author_email='christophe.haen@cern.ch',
    url='https://github.com/DIRACGrid/DIRACOS',
    license='GPLv3',
    entry_points={
        'console_scripts': ['dos-build-all-rpms=diracos.scripts.buildAll:main',
                            'dos-build-package=diracos.scripts.buildPackage:main',
                            'dos-build-python-modules=diracos.scripts.buildPythonModules:main',
                            'dos-set-rpaths=diracos.scripts.setRPATHWrapper:main',
                            'dos-bundle=diracos.scripts.bundleDiracOS:main',
                            'dos-dump-config=diracos.scripts.dumpConfig:main',
                            'dos-fix-pip-versions=diracos.scripts.fixPipRequirementsVersions:main',
                            'dos-build-extension=diracos.scripts.buildDiracOSExtension:main',
                            ],
    },
    packages=packages,
    package_dir=package_dir,
    package_data={'diracos': ['scriptTemplates/*']},
)
