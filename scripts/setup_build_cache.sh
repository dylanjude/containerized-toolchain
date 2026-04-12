#!/bin/bash

source spenv.sh

export HPCX_HOME=/tc/hpcx

echo "Spack installing cfdtc"
spack install cfdtc

echo "Generating activate.sh"
spack load --sh cfdtc > activate.sh

echo ""
echo "Done. Source activate.sh to load the environment:"
echo "  source activate.sh"

# spack buildcache push --unsigned ./spack_cache cfdtc
