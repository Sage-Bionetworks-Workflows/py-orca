#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

pipx run --spec 'tox~=3.0' tox -e clean,build

TARBALL_PATH=$(ls dist/*.tar.gz)
export TARBALL_PATH

docker build \
    -t orca \
    -f "${SCRIPT_DIR}/Dockerfile" \
    --build-arg TARBALL_PATH \
    "${SCRIPT_DIR}/../.."
