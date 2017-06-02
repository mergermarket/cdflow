#!/bin/bash

set -euo pipefail

image_id=cdflow-wrapper.test

docker build -t "${image_id}" .

docker run --rm -it --name "${image_id}" "${image_id}" \
    py.test \
    --cov=. \
    --cov-report term-missing \
    "${@}"

docker run --rm -it --name "${image_id}" "${image_id}" \
    flake8 --max-complexity=5
