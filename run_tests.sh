export LIBCLANG_PATH=/Users/jon/DEV/LLVM/build-ninja/lib/libclang.dylib
export PYTHONPATH=/Users/jon/DEV/LLVM/src/tools/clang/bindings/python:$PYTHONPATH
python -m unittest discover -v tests/
