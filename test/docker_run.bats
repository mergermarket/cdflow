#!/usr/bin/env bats

source src/cdflow
set +u

function setup {
    PATH="./test/mocks/:${PATH}"
}

@test "runs docker with flags" {
    export BATS_RESULTS="$(mktemp)"
    local expected="$(cat ./test/fixtures/docker_flags.output)"
    local project_root="/tmp/foo/"
    local environment_flags=" -e AWS_THING=foo"
    local image_id="cdflow-commands.local"
    docker_run "${project_root}" "${environment_flags}" "${image_id}"
    [[ "$(cat ${BATS_RESULTS})" == "${expected}" ]]
}
