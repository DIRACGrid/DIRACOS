#!/usr/bin/env python
import os
import subprocess
import sys

from diracos import SET_RPATH_PY_PATH


def main():
  """Create an environment for using py-lief and run set_RPATH.py"""
  known_missing_deps = os.path.abspath(sys.argv[1])
  proc = subprocess.Popen(
    'set -x && '
    'CONDA_BASE_TMP=$(mktemp -d) && '
    'cd ${CONDA_BASE_TMP} && '
    'curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && '
    'bash Miniconda3-latest-Linux-x86_64.sh -b -p "${CONDA_BASE_TMP}/miniconda" && '
    'cd - && '
    'source "${CONDA_BASE_TMP}/miniconda/bin/activate" && '
    'conda config --add channels conda-forge --env && '
    'conda install --yes python-magic py-lief tqdm && ' +
    SET_RPATH_PY_PATH + ' ' + known_missing_deps + ' && '
    'rm -rf "${CONDA_BASE_TMP}"',
    shell=True)
  proc.communicate()
  if proc.returncode != 0:
    raise RuntimeError(proc.returncode)


if __name__ == '__main__':
  main()
