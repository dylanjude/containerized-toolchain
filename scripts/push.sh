#!/bin/bash

source spenv.sh

echo "Adding mirror"
spack mirror add \
  --oci-username-variable GITHUB_USER \
  --oci-password-variable GHCR_TOKEN \
  ghcr \
  oci://ghcr.io/dylanjude/ctc-cache

echo "Pushing cfdtc to build cache"
spack buildcache push \
  --base-image ghcr.io/dylanjude/ctc-base:latest \
  --tag latest \
  --update-index \
  --unsigned \
  ghcr cfdtc

