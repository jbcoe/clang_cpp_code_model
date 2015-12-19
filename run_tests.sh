#!/usr/bin/env bash

export PYTHONPATH=${LLVM_SRC_ROOT}/tools/clang/bindings/python:${PYTHONPATH}

python -m unittest discover -v tests/
