#!/bin/bash

command="$0 $@"

container=""
spack_v=1.0.0 # spack version
hpcx="https://content.mellanox.com/hpc/hpc-x/v2.22/hpcx-v2.22-gcc-inbox-redhat8-cuda12-x86_64.tbz"
outdir="."
projdir=$(realpath .)
help=0
check=1

banner="-------------------------------------------------------------------"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -c|--container) container="$2"; shift ;;
        --hpcx) hpcx="$2"; shift ;;
        --spack_version) spack_v="$2"; shift ;;
        --prefix) outdir="$2"; shift ;;
        -h|--help) help=1 ;;
        -y) check=0 ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [ "$help" -eq 1 ]; then
    echo "Usage: generate.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  --container         Apptainer/Singularity sif file to use"
    echo "  --hpcx              HPCX download url or local path"
    echo "  --spack_version     Spack version to use (default 1.0.0)"
    echo "  --prefix            Directory to install to (default .)"
    echo ""
    exit
fi

if [[ "$container" == *.sif ]]; then
    container=$(realpath "$container")
    if [ ! -f "$container" ]; then
        echo "Container file not found: $container"
        exit 1
    fi
else
    if ! podman image exists "$container"; then
        echo "Podman image not found locally: $container"
        echo "Try: podman pull $container"
        echo ""
        echo "Available local images:"
        podman image list --format "  {{.Repository}}:{{.Tag}}"
        exit 1
    fi
fi

echo "Inputs:"
echo "  --container         $container"
echo "  --hpcx              $hpcx"
echo "  --spack_version     $spack_v"
echo "  --prefix            $outdir"
echo ""

BASE_DIR="${outdir}/tc"
count=1
while [[ -d "${BASE_DIR}${count}" ]]; do
    ((count++)) # Increment the counter
done
NEW_DIR="${BASE_DIR}${count}"

echo "Output dir: $NEW_DIR"
echo ""

if [ "$check" -eq 1 ]; then
    read -p "Continue? (y/N) " allgood
else
    allgood=y
fi

if [[ "$allgood" == [yY] ]]; then
    echo ""
else
    exit 0
fi

mkdir $NEW_DIR
cd $NEW_DIR

echo $banner
echo "Begin HPCX setup"
if [[ "$hpcx" =~ ^https?:// ]]; then
    echo "Fetching HPCX from URL..."    
    wget $hpcx
    for f in hpcx-v2*.tbz
    do
        hpcxtbz=$f
        break
    done
    if [ ! -f "$hpcxtbz" ];then
        echo "Could not download that HPCX tbz file"
        exit 1;
    fi
    hpcxdir="${hpcxtbz%.*}"
    echo "    Untarring $hpcxtbz ..."
    tar xf $hpcxtbz
    ln -s $hpcxdir "hpcx"
    
else
    echo "Sym-linking HPCX..."
    if [[ -d "$hpcx" ]]; then
        ln -s $hpcx hpcx
    else
        echo "HPCX dir does not exist: $hpcx"
        exit 1
    fi
fi
echo "HPCX setup complete"
echo ""
echo $banner
echo "Begin Spack setup"
if [ ! -d "spack-${spack_v}" ]; then
    if [ ! -f "spack-${spack_v}.tar.gz" ];then
        wget --no-check-certificate https://github.com/spack/spack/releases/download/v${spack_v}/spack-${spack_v}.tar.gz
    fi
    echo "    untarring spack ..."
    tar xzf spack-${spack_v}.tar.gz
    echo "    done"
fi
echo "Spack setup complete"

echo ""
echo $banner
echo ""

echo $command > generate_cmd.txt

cp -r ${projdir}/config .spack
cp -r ${projdir}/custom_repo .
cp ${projdir}/scripts/* .
chmod +x *.sh

if [[ -z "${container}" ]]; then
    echo "Container is not set, using current dir instead of container loc"
    sed -i "s@CTC_SETUP_DIR@${PWD}@g" .spack/repos.yaml
    sed -i "s@CTC_SETUP_DIR@${PWD}@g" .spack/modules.yaml
else
    sed -i "s@CTC_SETUP_DIR@/tc@g" .spack/repos.yaml
    sed -i "s@CTC_SETUP_DIR@/tc@g" .spack/modules.yaml

    if [[ "$container" == *.sif ]]; then
        # Apptainer/Singularity container
        # When hpcx is a local path the symlink in the tc dir points to an absolute
        # host path that won't resolve inside the container, so bind it explicitly.
        if [[ "$hpcx" =~ ^https?:// ]]; then
            hpcx_bind=""
        else
            hpcx_bind="--bind ${hpcx}:/tc/hpcx "
        fi

        install_cmd="apptainer exec ${hpcx_bind}--bind $PWD:/tc ${container} bash -c \"cd /tc && ./install.sh\""
        push_cmd="apptainer exec --env GITHUB_USER=\$GITHUB_USER --env GHCR_TOKEN=\$GHCR_TOKEN --bind $PWD:/tc ${container} bash -c \"cd /tc && ./push.sh\""
        shell_cmd="apptainer shell ${hpcx_bind}--bind $PWD:/tc ${container}"
    else
        # Podman container
        # When hpcx is a local path bind it explicitly into the container.
        # Podman/crun can't bind-mount over a symlink whose target is a host
        # path invisible to the container, so replace the symlink with an
        # empty directory to serve as a mountpoint.
        if [[ "$hpcx" =~ ^https?:// ]]; then
            hpcx_bind=""
        else
            rm -f hpcx
            mkdir hpcx
            hpcx_bind="--volume ${hpcx}:/tc/hpcx "
        fi

        install_cmd="podman run --rm -it --security-opt label=disable ${hpcx_bind}--volume $PWD:/tc ${container} bash -c \"cd /tc && ./install.sh\""
        push_cmd="podman run --rm -it --security-opt label=disable --env GITHUB_USER=\$GITHUB_USER --env GHCR_TOKEN=\$GHCR_TOKEN --volume $PWD:/tc ${container} bash -c \"cd /tc && ./push.sh\""
        shell_cmd="podman run --rm -it --security-opt label=disable ${hpcx_bind}--volume $PWD:/tc ${container} bash"
    fi

    {
        echo ""
        echo "# Install the toolchain:"
        echo "$install_cmd"
        echo ""
        echo "# Push to the build cache:"
        echo "$push_cmd"
        echo ""
        echo "# Run interactively:"
        echo "$shell_cmd"
    } >> generate_cmd.txt

    echo "Install the toolchain:"
    echo ""
    echo "\$ $install_cmd"
    echo ""
    echo "Push to the build cache:"
    echo ""
    echo "\$ $push_cmd"
    echo ""
    echo "Or run interactively with:"
    echo ""
    echo "\$ $shell_cmd"
    echo ""
    echo "(These commands are also saved in generate_cmd.txt)"
    echo ""
fi

echo "Toolchain directory setup complete"




