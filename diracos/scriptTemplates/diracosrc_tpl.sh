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
ARC_PLUGIN_PATH=$DIRACOS/usr/lib64/arc;
export ARC_PLUGIN_PATH;

# Gfal configuration
GFAL_CONFIG_DIR=$DIRACOS/etc/gfal2.d;
export GFAL_CONFIG_DIR;


# Gfal plugins
GFAL_PLUGIN_DIR=$DIRACOS/usr/lib64/gfal2-plugins/;
export GFAL_PLUGIN_DIR;
