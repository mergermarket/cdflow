#!/bin/bash

set -euo pipefail

IMAGE_ID="$(basename $(pwd))-build"

docker image build -t "${IMAGE_ID}" --target=build .

docker container run --rm --name "${IMAGE_ID}" \
    -i $(tty -s && echo -t) \
    -d \
    "${IMAGE_ID}"
    
docker container cp "${IMAGE_ID}:/cdflow/dist/cdflow" .

docker container rm --force "${IMAGE_ID}"
