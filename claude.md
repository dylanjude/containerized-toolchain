# Project Goal

The goal of this project is to have a container that can be pulled on
vast.ai and used to compile a cfd code so that it can be run
there. This project uses spack to build a toolchain. Right now the
toolchain is small but the idea is that it could get quite large and
complex later.

The spack toolchain is really just a bundle "cfdtc", which describes
which tools are needed. Once that package is built, I would push the
buildcache to an OCI registry and use a base image so that it can be
pulled on vast.

Both the image for building the toolchain and later pulling/running on
vast is based on nvidia/cuda:12.8.1-devel-rockylinux9. For building, i'm finding I need a few extra things so I created a "rocky_builder.sif" from the definition file:

'''
Bootstrap: docker
From: nvidia/cuda:12.8.1-devel-rockylinux9

%post
    dnf install -y dnf-plugins-core
    dnf config-manager --set-enabled crb
    dnf -y install gcc gcc-c++ make git gcc-gfortran wget bzip2 xz patch texinfo which unzip file
    dnf clean all
'''

I hope to setup the toolchain directory with:

sh generate.sh --hpcx ~/local/hpcx-v2.25.1-gcc-inbox-redhat9-cuda12-x86_64 --container ../rocky_builder.sif

And then run apptainer to do:

apptainer exec --bind /home/dylan/containers/ctc/tc1:/tc /home/dylan/containers/rocky_builder.sif cd /tc && ./setup_build_cache.sh

# The problem

Previously when I've used spack with hpcx, I wrote a hpcx-wrap spack
package which basically uses a HPCX_HOME environment variable to point
everything to the right directory. HPCX didn't actually sit in the
spack direcotry. Now when I try to build and eventually push the spack
cache to a registry, i want hpcx to go with it.