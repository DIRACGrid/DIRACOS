# This file is generated at bundle time

# If DIRACOS is not defined, define it as the directory
# in which the current script is stored

if [ -z $DIRACOS ];
then
  DIRACOS=$(dirname $(readlink -f "$BASH_SOURCE"));
  export DIRACOS;
fi

unset LD_LIBRARY_PATH

# Define the path
PATH=$DIRACOS/bin:$DIRACOS/usr/bin:$DIRACOS/sbin:$DIRACOS/usr/sbin:$PATH
export PATH

# Silence the python warnings
export PYTHONWARNINGS="ignore"

# ARC Computing Element
export ARC_LOCATION=$DIRACOS/usr
export ARC_LOCATION;

# Gfal configuration
GFAL_CONFIG_DIR=$DIRACOS/etc/gfal2.d;
export GFAL_CONFIG_DIR;

# Gfal plugins
GFAL_PLUGIN_DIR=$DIRACOS/usr/lib64/gfal2-plugins/;
export GFAL_PLUGIN_DIR;

# Davix options (will be default in the future)
export DAVIX_USE_LIBCURL=1

# Many Linux distributions set LESSOPEN to provide fancier features
# These don't work with the CentOS 6 version of less so unset the variable
unset LESSOPEN
