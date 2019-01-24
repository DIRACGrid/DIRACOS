#!/bin/bash

if [[ $CI_COMMIT_REF_NAME == rel-* ]]; then
  export BUILD_NAME=${CI_COMMIT_REF_NAME:4}
  export MAKE_TAG=true
else
  export BUILD_NAME=${CI_COMMIT_REF_NAME}
  export MAKE_TAG=false
fi
