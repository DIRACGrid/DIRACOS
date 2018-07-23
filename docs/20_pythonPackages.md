# Python packages

The python packages are installed with pip inside a mock environment, using virtualenv. Running inside the mock environment ensures to use the lib packages needed from our repo.

The python packages are installed from a requirement file, linked in the json configuration file (see `pipRequirements`). Adding a new python package is as simple as adding a line there.


## Adding a python package

As mentioned earlier, python packages are installed with `pip` from a requirement file linked in the json config file as `pipRequirements`.
To add a python package, just add it in the requirement file. However, in order to be able to build it in the mock and virtualenv environment, some building dependencies might be necessary. If so, they should be added in `pipBuildDependencies`.
