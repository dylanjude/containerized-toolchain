# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install occa
#
# You can edit this file again by typing:
#
#     spack edit occa
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class Occa(CMakePackage):
    """FIXME: Put a proper description of your package here."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://libocca.org"
    url = "https://github.com/libocca/occa/archive/refs/tags/v2.0.0.tar.gz"

    maintainers("dylanjude")
    license("MIT")

    version("2.0.0", sha256="f2521901fed5d199193d54c7db4186479a974bdae92ac97779c47fa2bb68badd")
    version("1.6.0", sha256="b863a24171000097121aff5c43dadf22416c143824598a51c653689fd917794f")
    version("1.5.0", sha256="b939f826f3e970b45aa77089568995399355fcdad3bc787b60cf73eb4962b0b7")
    version("1.4.0", sha256="5995288615f45dd2cf2f3e13b9e04c3b89edde1e014d36c6da014c11b9adb4a7")

    variant("cuda",   default=True,  description="Activates support for CUDA")
    variant("hip",    default=False, description="Activates support for HIP")    
    variant("openmp", default=True,  description="Activates support for OpenMP")
    variant("opencl", default=False, description="Activates support for OpenCL")
    variant("dpcpp",  default=False, description="Activates support for DPCPP")

    depends_on("c", type="build")
    depends_on("cxx", type="build")

    depends_on("cuda", when="+cuda")
    depends_on("hip", when="+hip")

    depends_on("cmake", type="build")

    # OCCA_ENABLE_CUDA:BOOL=ON
    # OCCA_ENABLE_DPCPP:BOOL=ON
    # OCCA_ENABLE_EXAMPLES:BOOL=OFF
    # OCCA_ENABLE_FORTRAN:BOOL=OFF
    # OCCA_ENABLE_HIP:BOOL=ON
    # OCCA_ENABLE_METAL:BOOL=ON
    # OCCA_ENABLE_OPENCL:BOOL=ON
    # OCCA_ENABLE_OPENMP:BOOL=ON
    # OCCA_ENABLE_TESTS:BOOL=OFF

    # FIXME: Add dependencies if required.
    # depends_on("foo")

    def cmake_args(self):
        # FIXME: Add arguments other than
        # FIXME: CMAKE_INSTALL_PREFIX and CMAKE_BUILD_TYPE
        # FIXME: If not needed delete this function
        args = [
            self.define("CMAKE_BUILD_TYPE", "Release"),
            self.define_from_variant("OCCA_ENABLE_CUDA", "cuda"),
            self.define_from_variant("OCCA_ENABLE_HIP", "hip"),
            self.define_from_variant("OCCA_ENABLE_OPENMP", "openmp"),
            self.define_from_variant("OCCA_ENABLE_OPENCL", "opencl"),
            self.define_from_variant("OCCA_ENABLE_DPCPP", "dpcpp"),
        ]
        return args

    def setup_dependent_build_environment(self, env, dependent_spec):
        env.set("OCCA_INSTALL_DIR", self.prefix)
        env.set("OCCA_DIR", self.prefix)        
        env.set("OCCA_HOME", self.prefix)        

    def setup_run_environment(self, env):
        env.set("OCCA_INSTALL_DIR", self.prefix)
        env.set("OCCA_DIR", self.prefix)        
        env.set("OCCA_HOME", self.prefix)        
    
