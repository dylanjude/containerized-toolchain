#!/bin/bash

# Source this file to use spack

# override the ~/.spack and system spack directories in case there's
# something conflicting there

# find the spack dir:

for d in spack-[0-9]*
do
    spackdir=$d
    break
done

echo "Sourcing spack env from ${spackdir} "

export SPACK_USER_CONFIG_PATH=${PWD}/.spack
export SPACK_SYSTEM_CONFIG_PATH=${PWD}/.system_spack
export SPACK_USER_CACHE_PATH=${PWD}/.spack_cache

# source the spack environment

source ${PWD}/${spackdir}/share/spack/setup-env.sh

echo "Done"


