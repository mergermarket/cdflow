#!/bin/bash

set -euo pipefail

IMAGE_ID="$(basename $(pwd))-acceptance-test"
AC_FOLDER="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

docker image build -t "${IMAGE_ID}" \
    --build-arg CDFLOW_COMMIT_SHA=${CDFLOW_COMMIT_SHA:-master} \
    --build-arg ALWAYS_INVALIDATE_BUILD_CACHE_HERE=$(date +%Y%m%d%H%M%S) \
    $AC_FOLDER

root=$(git rev-parse --show-toplevel)

echo "Running the acceptance tests within the ${IMAGE_ID} container"

if [ -n "${DOCKERHUB_USERNAME:-}" ] && [ -n "${DOCKERHUB_USERNAME:-}" ]; then
    docker container run \
        --name "${IMAGE_ID}" \
        --rm \
        -e CDFLOW_IMAGE_ID=${CDFLOW_IMAGE_ID:-mergermarket/cdflow-commands:latest} \
        -e DOCKERHUB_USERNAME=${DOCKERHUB_USERNAME} \
        -e DOCKERHUB_PASSWORD=${DOCKERHUB_PASSWORD} \
        -w $AC_FOLDER \
        -v ${root}:${root} \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -i $(tty >/dev/null && echo -t) \
        "${IMAGE_ID}" cdflow --help
elif [ -e ~/.docker/config.json ]; then
    docker container run \
        --name "${IMAGE_ID}" \
        --rm \
        -e CDFLOW_IMAGE_ID=${CDFLOW_IMAGE_ID:-mergermarket/cdflow-commands:latest} \
        -w $AC_FOLDER \
        -v ${root}:${root} \
        -v ~/.docker/config.json:/root/.docker/config.json \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -i $(tty >/dev/null && echo -t) \
        "${IMAGE_ID}" cdflow --help
else
    docker container run \
        --name "${IMAGE_ID}" \
        --rm \
        -e CDFLOW_IMAGE_ID=${CDFLOW_IMAGE_ID:-mergermarket/cdflow-commands:latest} \
        -w $AC_FOLDER \
        -v ${root}:${root} \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -i $(tty >/dev/null && echo -t) \
        "${IMAGE_ID}" cdflow --help
fi