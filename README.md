# clang_cpp_code_model
Python functions and classes built on top of the existing python bindings for libclang that give a simple representation of C++ classes and functions.

This module was writtent to power code generators, see <https://github.com/jbcoe/C_API_generation> for an example.


# Requires
* libclang 3.8 <http://llvm.org/releases/>
* python module clang==3.8 <https://pypi.python.org/pypi/clang/3.8>


# Usage
Set LD_LIBRARY_PATH to find libclang   
    ./run_tests.sh
