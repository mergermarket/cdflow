# CDFlow

## Introduction

CDFlow is a tool that enables continuous delivery of software components using [Terraform](https://www.terraform.io/) to manage their virtual infrastructure. CDFlow creates a release artifact containing everything required to deploy the software which can be carried through a continuous delivery pipeline. It can build, deploy and destroy your applications through code, allowing you to manage versions of your infrastructure through source control.

## Contributing

Contributions are welcome; we encourage you raise issues and pull requests to help us make CDFlow better.

For pull requests, we require a tests to replicate your issue or feature and to follow our style guide. We use PEP 8 style for Python and have a linter that should display any issues. You can run the tests with the `/test.sh` script in the root of both the [cdflow](https://github.com/mergermarket/cdflow) and [cdflow-commands](https://github.com/mergermarket/cdflow-commands) when making changes.
