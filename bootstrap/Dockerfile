FROM nvidia/cuda:12.8.1-devel-rockylinux9

RUN dnf install -y dnf-plugins-core && \
    dnf config-manager --set-enabled crb && \
    dnf install -y gcc gcc-c++ make git gcc-gfortran wget bzip2 xz patch texinfo which unzip file python3-devel zlib-devel openssl-devel bzip2-devel xz-devel libzstd-devel ncurses-devel readline-devel libcurl-devel && \
    dnf clean all