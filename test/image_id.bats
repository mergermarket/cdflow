#!/usr/bin/env bats

source src/cdflow
set +u

@test "uses latest docker tag by default" {
    local image_id=$(get_image_id)
    [[ "${image_id}" == "mergermarket/cdflow-commands:latest" ]]
}

@test "uses local docker image when debug set" {
    CDFLOW_DEBUG=1
    local image_id=$(get_image_id)
    [[ "${image_id}" == "cdflow-commands.local" ]]
}
