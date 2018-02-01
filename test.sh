#!/bin/bash

set -euo pipefail

image_id="$(basename $(pwd))"

docker build -t "${image_id}" .

if [ ${1} != 'lint-only' ]
then
    docker run --rm --name "${image_id}" \
        -i $(tty -s && echo -t) \
        "${image_id}" \
        py.test \
        --cov=. \
        --cov-report term-missing \
        "${@}"
fi

docker run --rm --name "${image_id}" "${image_id}" \
    flake8 --max-complexity=5
