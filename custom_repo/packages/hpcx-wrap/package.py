# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack.package import *

class HpcxWrap(Package):
    """The HPC-X MPI implementation from NVIDIA/Mellanox based on OpenMPI.
    This package copies the HPCX tree into the spack prefix so it can be
    pushed to a build cache and used without HPCX_HOME on the target machine."""

    homepage = "https://developer.nvidia.com/networking/hpc-x"
    maintainers("dylanjude")

    has_code = False
    version("99.99")

    provides("mpi")

    def install(self, spec, prefix):
        hpcx_dir = os.environ.get("HPCX_HOME")
        if not hpcx_dir:
            raise InstallError(
                "HPCX_HOME environment variable is not set. "
                "Point it to the root of the HPCX installation before running spack install."
            )
        if not os.path.isdir(hpcx_dir):
            raise InstallError(f"HPCX_HOME='{hpcx_dir}' is not a valid directory.")
        install_tree(hpcx_dir, prefix)

    @property
    def headers(self):
        mpi_dir = os.path.join(self.prefix, "ompi")
        hdrs = find_headers("mpi", os.path.join(mpi_dir, "include"), recursive=False)
        if not hdrs:
            hdrs = HeaderList([os.path.join(mpi_dir, "include", "mpi.h")])
        hdrs.directories = [os.path.join(mpi_dir, "include")]
        return hdrs

    @property
    def libs(self):
        mpi_dir = os.path.join(self.prefix, "ompi")
        mpi_libs = find_libraries(["libmpi"], os.path.join(mpi_dir, "lib"), shared=True, recursive=False)
        if not mpi_libs:
            mpi_libs = LibraryList([os.path.join(mpi_dir, "lib", "libmpi.so")])
        return mpi_libs

    def setup_dependent_package(self, module, dependent_spec):
        mpi_bin = os.path.join(self.prefix, "ompi", "bin")
        self.spec.mpicc  = os.path.join(mpi_bin, "mpicc")
        self.spec.mpicxx = os.path.join(mpi_bin, "mpicxx")
        self.spec.mpif77 = os.path.join(mpi_bin, "mpif77")
        self.spec.mpifc  = os.path.join(mpi_bin, "mpif90")

    def make_base_environment(self, prefix, env):
        hpcx_dir = str(prefix)
        hpcx_mpi_dir = os.path.join(hpcx_dir, "ompi")

        env.set("HPCX_HOME", hpcx_dir)
        env.set("HPCX_UCX_DIR", os.path.join(hpcx_dir, "ucx", "mt"))
        env.set("HPCX_UCC_DIR", os.path.join(hpcx_dir, "ucc"))
        env.set("HPCX_SHARP_DIR", os.path.join(hpcx_dir, "sharp"))
        env.set("HPCX_HCOLL_DIR", os.path.join(hpcx_dir, "hcoll"))
        env.set("HPCX_NCCL_RDMA_SHARP_PLUGIN_DIR", os.path.join(hpcx_dir, "nccl_rdma_sharp_plugin"))
        env.set("HPCX_CLUSTERKIT_DIR", os.path.join(hpcx_dir, "clusterkit"))
        env.set("HPCX_MPI_DIR", hpcx_mpi_dir)
        env.set("HPCX_OSHMEM_DIR", hpcx_mpi_dir)
        env.set("HPCX_IPM_DIR", os.path.join(hpcx_mpi_dir, "tests", "ipm-2.0.6"))
        env.set("HPCX_IPM_LIB", os.path.join(hpcx_mpi_dir, "tests", "ipm-2.0.6", "lib", "libipm.so"))
        env.set("HPCX_MPI_TESTS_DIR", os.path.join(hpcx_mpi_dir, "tests"))
        env.set("HPCX_OSU_DIR", os.path.join(hpcx_mpi_dir, "tests", "osu-micro-benchmarks-5.8"))
        env.set("HPCX_OSU_CUDA_DIR", os.path.join(hpcx_mpi_dir, "tests", "osu-micro-benchmarks-5.8-cuda"))

        env.prepend_path("PATH", os.path.join(hpcx_dir, "ucx", "mt", "bin"))
        env.prepend_path("PATH", os.path.join(hpcx_dir, "ucc", "bin"))
        env.prepend_path("PATH", os.path.join(hpcx_dir, "hcoll", "bin"))
        env.prepend_path("PATH", os.path.join(hpcx_dir, "sharp", "bin"))
        env.prepend_path("PATH", os.path.join(hpcx_mpi_dir, "tests", "imb"))
        env.prepend_path("PATH", os.path.join(hpcx_dir, "clusterkit", "bin"))

        env.prepend_path("LD_LIBRARY_PATH", os.path.join(hpcx_dir, "ucx", "mt", "lib"))
        env.prepend_path("LD_LIBRARY_PATH", os.path.join(hpcx_dir, "ucx", "mt", "lib", "ucx"))
        env.prepend_path("LD_LIBRARY_PATH", os.path.join(hpcx_dir, "ucc", "lib"))
        env.prepend_path("LD_LIBRARY_PATH", os.path.join(hpcx_dir, "ucc", "lib", "ucc"))
        env.prepend_path("LD_LIBRARY_PATH", os.path.join(hpcx_dir, "hcoll", "lib"))
        env.prepend_path("LD_LIBRARY_PATH", os.path.join(hpcx_dir, "sharp", "lib"))
        env.prepend_path("LD_LIBRARY_PATH", os.path.join(hpcx_dir, "nccl_rdma_sharp_plugin", "lib"))

        env.prepend_path("LIBRARY_PATH", os.path.join(hpcx_dir, "ucx", "mt", "lib"))
        env.prepend_path("LIBRARY_PATH", os.path.join(hpcx_dir, "ucc", "lib"))
        env.prepend_path("LIBRARY_PATH", os.path.join(hpcx_dir, "hcoll", "lib"))
        env.prepend_path("LIBRARY_PATH", os.path.join(hpcx_dir, "sharp", "lib"))
        env.prepend_path("LIBRARY_PATH", os.path.join(hpcx_dir, "nccl_rdma_sharp_plugin", "lib"))

        env.prepend_path("CPATH", os.path.join(hpcx_dir, "hcoll", "include"))
        env.prepend_path("CPATH", os.path.join(hpcx_dir, "sharp", "include"))
        env.prepend_path("CPATH", os.path.join(hpcx_dir, "ucx", "mt", "include"))
        env.prepend_path("CPATH", os.path.join(hpcx_dir, "ucc", "include"))
        env.prepend_path("CPATH", os.path.join(hpcx_mpi_dir, "include"))

        env.prepend_path("PKG_CONFIG_PATH", os.path.join(hpcx_dir, "hcoll", "lib", "pkgconfig"))
        env.prepend_path("PKG_CONFIG_PATH", os.path.join(hpcx_dir, "sharp", "lib", "pkgconfig"))
        env.prepend_path("PKG_CONFIG_PATH", os.path.join(hpcx_dir, "ucx", "mt", "lib", "pkgconfig"))
        env.prepend_path("PKG_CONFIG_PATH", os.path.join(hpcx_mpi_dir, "lib", "pkgconfig"))

        env.prepend_path("MANPATH", os.path.join(hpcx_mpi_dir, "share", "man"))

        env.set("OPAL_PREFIX", hpcx_mpi_dir)
        env.set("PMIX_INSTALL_PREFIX", hpcx_mpi_dir)
        env.set("OMPI_HOME", hpcx_mpi_dir)
        env.set("MPI_HOME", hpcx_mpi_dir)
        env.set("OSHMEM_HOME", hpcx_mpi_dir)
        env.set("SHMEM_HOME", hpcx_mpi_dir)

        env.prepend_path("PATH", os.path.join(hpcx_mpi_dir, "bin"))
        env.prepend_path("LD_LIBRARY_PATH", os.path.join(hpcx_mpi_dir, "lib"))
        env.prepend_path("LIBRARY_PATH", os.path.join(hpcx_mpi_dir, "lib"))

    def setup_dependent_build_environment(self, env, dependent_spec):
        self.make_base_environment(self.prefix, env)

    def setup_run_environment(self, env):
        self.make_base_environment(self.prefix, env)
