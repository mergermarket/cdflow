#!/bin/bash

set -euo pipefail

image_id=cdflow-wrapper.test

docker build -t "${image_id}" .
docker run --rm -it --name "${image_id}" "${image_id}" py.test "${@}"
