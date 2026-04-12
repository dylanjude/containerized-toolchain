#!/bin/bash

source spenv.sh

export HPCX_HOME=/tc/hpcx

echo "Spack installing cfdtc"
spack install cfdtc
