#!/usr/bin/env bats

source src/cdflow
set +u

@test "sets up AWS access key" {
    AWS_ACCESS_KEY_ID="foo"
    local environment_flags=$(get_environment_flags)
    [[ "${environment_flags}" == " -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" ]]
}

@test "sets up AWS secret key" {
    AWS_SECRET_ACCESS_KEY="bar"
    local environment_flags=$(get_environment_flags)
    [[ "${environment_flags}" == " -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" ]]
}

@test "sets up AWS session token" {
    AWS_SESSION_TOKEN="bat"
    local environment_flags=$(get_environment_flags)
    [[ "${environment_flags}" == " -e AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}" ]]
}

@test "sets up Fastly API key" {
    FASTLY_API_KEY="baz"
    local environment_flags=$(get_environment_flags)
    [[ "${environment_flags}" == " -e FASTLY_API_KEY=${FASTLY_API_KEY}" ]]
}

@test "passes through job name" {
    JOB_NAME="biz"
    local environment_flags=$(get_environment_flags)
    [[ "${environment_flags}" == " -e JOB_NAME=${JOB_NAME}" ]]
}

@test "passes through email" {
    EMAIL="foo@bar.com"
    local environment_flags=$(get_environment_flags)
    [[ "${environment_flags}" == " -e EMAIL=${EMAIL}" ]]
}

@test "gets email from git when not in environment" {
    unset EMAIL
    git config --global --add user.email "foo@bar.baz"
    local environment_flags=$(get_environment_flags)
    [[ "${environment_flags}" == " -e EMAIL=foo@bar.baz" ]]
}

@test "sets all environment flags when present" {
    AWS_ACCESS_KEY_ID="foo"
    AWS_SECRET_ACCESS_KEY="bar"
    AWS_SESSION_TOKEN="bat"
    FASTLY_API_KEY="baz"
    JOB_NAME="biz"
    EMAIL="foo@bar.com"
    local environment_flags=$(get_environment_flags)
    local expected_flags=" -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}"
    expected_flags="${expected_flags} -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}"
    expected_flags="${expected_flags} -e AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}"
    expected_flags="${expected_flags} -e FASTLY_API_KEY=${FASTLY_API_KEY}"
    expected_flags="${expected_flags} -e JOB_NAME=${JOB_NAME}"
    expected_flags="${expected_flags} -e EMAIL=${EMAIL}"
    [[ "${environment_flags}" == "${expected_flags}" ]]
}
