# This file is generated at bundle time

# If DIRACOS is not defined, define it as the directory
# in which the current script is stored

if [ -z $DIRACOS ];
then
  DIRACOS=$(dirname $(readlink -f "$BASH_SOURCE"));
  export DIRACOS;
fi


# Define the LD_LIBRARY_PATH
LD_LIBRARY_PATH=DIRACOS_LD_LIBRARY_PATH:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH

# Define the path
PATH=$DIRACOS/bin:$DIRACOS/usr/bin:$DIRACOS/sbin:$DIRACOS/usr/sbin:$PATH
export PATH

# Silence the python warnings
export PYTHONWARNINGS="ignore"
