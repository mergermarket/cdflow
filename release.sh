#!/bin/bash

set -euo pipefail

IMAGE_ID="$(basename $(pwd))-release"

docker image build -t "${IMAGE_ID}" .

docker container run --rm --name "${IMAGE_ID}" \
    -i $(tty -s && echo -t) \
    -e TWINE_USERNAME=__token__ \
    -e TWINE_PASSWORD \
    "${IMAGE_ID}" \
        ./publish.sh
