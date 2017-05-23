#!/bin/bash

image_id=cdflow-wrapper.test

docker build -t "${image_id}" .
docker run --rm -it --name "${image_id}" "${image_id}" "${@}" test
