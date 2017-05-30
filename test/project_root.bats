#!/usr/bin/env bats

source src/cdflow
set +u

@test "gets project root from git" {
    local expected_root=$(mktemp -d)
    cd "${expected_root}" && git init
    local project_root=$(get_project_root)
    [[ "${project_root}" == "${expected_root}" ]]
}

@test "get project root from environment variable" {
    CDFLOW_PROJECT_ROOT="/tmp/foo/bar"
    local project_root=$(get_project_root)
    [[ "${project_root}" == "${CDFLOW_PROJECT_ROOT}" ]]
}
