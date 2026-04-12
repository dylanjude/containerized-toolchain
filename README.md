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

This section is only necessary if you don't like my existing base
container at: ghcr.io/dylanjude/ctc-base:latest . If you're fine with
it, skip to the "apptainer pull ..." command at the end of this
section.

Both building and running are based on
`nvidia/cuda:12.8.1-devel-rockylinux9`.  Building requires a few extra
system packages, so a builder image is needed. This needs to be a
Docker-native container so it can't be built with singularity. Make a
new directory and in there make a "Dockerfile" that looks like this:

```
FROM nvidia/cuda:12.8.1-devel-rockylinux9

RUN dnf install -y dnf-plugins-core && \
    dnf config-manager --set-enabled crb && \
    dnf install -y gcc gcc-c++ make git gcc-gfortran wget bzip2 xz patch texinfo which unzip file && \
    dnf clean all

```

From there using podman you do:

```bash
podman login ghcr.io --username dylanjude --password $GHCR_TOKEN
```

```bash
podman build --security-opt label=disable -t ghcr.io/dylanjude/ctc-base:latest .
```

And push:

```bash
podman push ghcr.io/dylanjude/ctc-base:latest
```

This container can now be "pulled" and used by either podman, docker,
or apptainer to build the actual spack toolchain. I find apptainer the
most intuitive so in some known directory, you would do:

```bash
apptainer pull docker://ghcr.io/dylanjude/ctc-base:latest
```

This will give you a ctc-base_latest.sif file. The rest of this
project assumes at the ctc-base_latest.sif file is in the parent
directory of this repository.

## HPCX

HPCX is handled by the custom `hpcx-wrap` spack package. During `spack install`
it copies the entire HPCX tree into the spack prefix, making the install
self-contained and pushable to a build cache. `HPCX_HOME` must be set to the
HPCX root before installing (handled automatically by `install.sh`).

## Workflow

### 1. Generate a toolchain directory

```bash
sh generate.sh --hpcx /path/to/untarred/hpcx --container ../ctc-base_latest.sif
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

### 2. Install the toolchain

The generate script prints the exact apptainer command to run. It looks like:

```bash
apptainer exec \
  --bind /path/to/hpcx:/tc/hpcx \
  --bind /path/to/tc1:/tc \
  ../ctc-base_latest.sif \
  bash -c "cd /tc && ./install.sh"
```

`install.sh` runs `spack install cfdtc`. When the build cache is later pulled
on a target machine, paths are set correctly out of the box.

### 3. Push to a build cache

```bash
apptainer exec \
  --env GITHUB_USER=$GITHUB_USER \
  --env GHCR_TOKEN=$GHCR_TOKEN \
  --bind /path/to/tc1:/tc \
  ../ctc-base_latest.sif \
  bash -c "cd /tc && ./push.sh"
```

`push.sh` does two things:

1. Registers the OCI mirror with `spack mirror add`, passing credentials via
   `GITHUB_USER` and `GHCR_TOKEN` environment variables (a GitHub personal
   access token with `write:packages` scope). Spack reads these at push time
   rather than storing credentials on disk.

2. Pushes `cfdtc` and all dependencies with `spack buildcache push`, tagging
   the result against `ghcr.io/dylanjude/ctc-base:latest` as the base image
   and updating the cache index. The HPCX bind mount is not needed for this
   step since HPCX is already baked into the spack store.

### 4. Pull on a remote machine

On the target machine, add the mirror in read-only mode (no credentials needed
for a public registry) and install:

```bash
spack mirror add ghcr oci://ghcr.io/dylanjude/ctc-cache
spack install cfdtc
```

Spack will pull all packages from the cache rather than building from source.

## Repository layout

```
config/             Spack user config (packages, modules, repos, config)
custom_repo/        Custom spack packages
  packages/
    cfdtc/          Bundle package defining the toolchain
    hpcx-wrap/      Wraps HPCX into spack by copying it into the prefix
    occa/           OCCA GPU portability layer (optional)
scripts/
  install.sh             Runs spack install cfdtc
  push.sh                Pushes the built packages to the configured OCI mirror
  spenv.sh               Sources spack, isolating it from system/user config
generate.sh         Sets up a new tc<N> build directory
```

