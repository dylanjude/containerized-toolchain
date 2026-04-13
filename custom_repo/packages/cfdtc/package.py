from spack.package import *

class Cfdtc(BundlePackage):
    """Run-time and developer toolchain for CFD codes"""

    homepage = "https://github.com/dylanjude/containerized-toolchain"
    # There is no URL since there is no code to download.

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    maintainers("dylanjude")

    version("0.1.0")

    # depends_on("cmake")
    depends_on("mpi")
    depends_on("cuda")
    depends_on("python")
    depends_on("py-mpi4py")
    depends_on("py-numpy")
    depends_on("py-pybind11")
    depends_on("py-pyyaml")
    depends_on("py-pip")
    depends_on("occa")

    # There is no need for install() since there is no code.
