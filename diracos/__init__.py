from os import path

# Location of the script templates
SCRIPT_TPL_PATH = path.join(path.dirname(path.realpath(__file__)), 'scriptTemplates')

# The script template to build the python module
BUILD_PYTHON_MODULE_SH_TPL_PATH = path.join(SCRIPT_TPL_PATH, 'build_python_module_tpl.sh')

# Tpl to freeze the versions of the pip modules we will use
FIX_PIP_REQUIREMENTS_VERSIONS_SH_TPL_PATH = path.join(SCRIPT_TPL_PATH, 'fix_pip_requirements_versions_tpl.sh')

# Script for setting RPATH for all ELF binaries
SET_RPATH_PY_PATH = path.join(SCRIPT_TPL_PATH, 'set_RPATH.py')

# Tpl script to make a bundle of everything
BUNDLE_DIRACOS_SCRIPT_SH_TPL_PATH = path.join(SCRIPT_TPL_PATH, 'bundle_diracos_script_tpl.sh')

# Tpl script of diracosrc
DIRACOSRC_TPL_PATH = path.join(SCRIPT_TPL_PATH, 'diracosrc_tpl.sh')

# The python bundling script that we have to put in the mock environment
PYTHON_BUNDLE_LIB_PATH = path.join(path.dirname(path.realpath(__file__)), 'bundlelib.py')

# Tpl script to build a DIRACOS extension
BUILD_DIRACOS_EXTENSION_TPL_PATH = path.join(SCRIPT_TPL_PATH, 'build_diracos_extension_tpl.sh')
