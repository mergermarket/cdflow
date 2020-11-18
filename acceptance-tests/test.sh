#!/bin/bash

set -euo pipefail

IMAGE_ID="$(basename $(pwd))-acceptance-test"
AC_FOLDER="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

docker image build -t "${IMAGE_ID}" \
    --build-arg CDFLOW_COMMIT_SHA=${CDFLOW_COMMIT_SHA:-master} \
    --build-arg ALWAYS_INVALIDATE_BUILD_CACHE_HERE=$(date +%Y%m%d%H%M%S) \
    $AC_FOLDER

root=$(git rev-parse --show-toplevel)

docker container run \
    --name "${IMAGE_ID}" \
    --rm \
    -e CDFLOW_IMAGE_ID=${CDFLOW_IMAGE_ID:-mergermarket/cdflow-commands:latest} \
    -w $AC_FOLDER \
    -v ${root}:${root} \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -i $(tty >/dev/null && echo -t) \
    "${IMAGE_ID}" cdflow --help
