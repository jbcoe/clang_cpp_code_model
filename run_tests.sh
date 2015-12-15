export LD_LIBRARY_PATH=/Users/jon/DEV/LLVM/build-ninja/lib/:$LD_LIBRARY_PATH
export PYTHONPATH=/Users/jon/DEV/LLVM/src/tools/clang/bindings/python:$PYTHONPATH
python -m nose -v tests/
