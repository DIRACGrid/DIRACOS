# This is the setup.py used to package the deployment script
# and fetch the needed dependecy

import os
from setuptools import setup, find_packages


base_dir = os.path.dirname(__file__)
setup(
    name='diracos',
    description='Tools to build DIRACOS',
    version="1.0.0",
    author='Christophe Haen',
    author_email='christophe.haen@cern.ch',
    url='https://github.com/DIRACGrid/DIRACOS',
    license='GPLv3',
    entry_points={
        'console_scripts': ['dos-build-all-rpms=scripts.buildAll:main',
                            'dos-build-package=scripts.buildPackage:main',
                            'dos-build-python-modules=scripts.buildPythonModules:main',
                            'dos-bundle=scripts.bundleDiracOS:main',
                            'dos-dump-config=scripts.dumpConfig:main',
                            'dos-fix-pip-versions=scripts.fixPipRequirementsVersions:main'
                             ],
    },
    packages=find_packages(),
    package_data = {'diracos': ['scriptTemplates/*']},
)
