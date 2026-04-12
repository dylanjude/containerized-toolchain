# CFD Toolchain Container (ctc)

Builds a portable CFD toolchain using [Spack](https://spack.io) inside an
Apptainer container. The goal is to produce a self-contained spack build cache
that can be pushed to an OCI registry and pulled on a remote GPU node (e.g.
vast.ai) without needing to rebuild anything.

The toolchain is defined by the `cfdtc` spack bundle package, which lists the
required dependencies. Currently it includes HPCX MPI and CUDA; other packages
(cmake, OCCA, numpy, etc.) are stubbed out and can be uncommented as the
toolchain grows.

## Base container

Both building and running are based on `nvidia/cuda:12.8.1-devel-rockylinux9`.
Building requires a few extra system packages, so a builder image is needed.
Create it with:

```
Bootstrap: docker
From: nvidia/cuda:12.8.1-devel-rockylinux9

%post
    dnf install -y dnf-plugins-core
    dnf config-manager --set-enabled crb
    dnf -y install gcc gcc-c++ make git gcc-gfortran wget bzip2 xz patch texinfo which unzip file
    dnf clean all
```

Build the SIF:

```bash
apptainer build rocky_builder.sif rocky_builder.def
```

## HPCX

HPCX is handled by the custom `hpcx-wrap` spack package. During `spack install`
it copies the entire HPCX tree into the spack prefix, making the install
self-contained and pushable to a build cache. `HPCX_HOME` must be set to the
HPCX root before installing (handled automatically by `setup_build_cache.sh`).

## Workflow

### 1. Generate a toolchain directory

```bash
sh generate.sh --hpcx /path/to/hpcx --container /path/to/rocky_builder.sif
```

This creates a numbered `tc<N>/` directory containing a self-contained spack
installation, the custom package repo, and all build scripts. HPCX can be a
local directory path or a download URL.

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--hpcx` | HPC-X v2.22 URL | Local path or download URL for HPCX |
| `--container` | *(none)* | Apptainer SIF file to use |
| `--spack_version` | `1.0.0` | Spack version to download |
| `--prefix` | `.` | Parent directory for the `tc<N>` output |
| `-y` | *(off)* | Skip confirmation prompt |

### 2. Build the toolchain

The generate script prints the exact apptainer command to run. It looks like:

```bash
apptainer exec \
  --bind /path/to/hpcx:/tc/hpcx \
  --bind /path/to/tc1:/tc \
  rocky_builder.sif \
  bash -c "cd /tc && ./setup_build_cache.sh"
```

`setup_build_cache.sh` runs `spack install cfdtc` and then generates an
`activate.sh` in the tc directory using `spack load --sh`.

### 3. Use the toolchain

Source `activate.sh` to put MPI wrappers, libraries, and all environment
variables on the correct paths. No spack required at this point.

```bash
source /path/to/tc1/activate.sh
mpicc mycode.c -o mycode
```

### 4. Push to a build cache (TODO)

```bash
spack buildcache push --unsigned <oci-registry-url> cfdtc
```

## Repository layout

```
config/             Spack user config (packages, modules, repos, config)
custom_repo/        Custom spack packages
  packages/
    cfdtc/          Bundle package defining the toolchain
    hpcx-wrap/      Wraps HPCX into spack by copying it into the prefix
    occa/           OCCA GPU portability layer (optional)
scripts/
  setup_build_cache.sh   Runs spack install and generates activate.sh
  spenv.sh               Sources spack, isolating it from system/user config
generate.sh         Sets up a new tc<N> build directory
```

## Known limitation

Build paths are tied to the `/tc` bind mount used during the build. Pushing to
an OCI registry and pulling into a fresh container will require either
configuring the target container to install at the same path, or using spack's
build cache relocation support.
