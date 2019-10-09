# CDFlow

## Introduction

CDFlow is a tool that enables continuous delivery of software components using [Terraform](https://www.terraform.io/) to manage their virtual infrastructure. CDFlow creates a release artifact containing everything required to deploy the software which can be carried through a continuous delivery pipeline. It can build, deploy and destroy your applications through code, allowing you to manage versions of your infrastructure through source control.

## Overview

CDFlow has 2 main phases: _release_ and _deploy_. When the `cdflow release` command is run the tool builds an artifact - either a [Docker image](https://docs.docker.com/glossary/?term=image) or a zip file containing code for an [AWS Lambda](https://aws.amazon.com/lambda/) function - and publishes that, to either [ECR](https://aws.amazon.com/ecr/) or an [S3](https://aws.amazon.com/s3/) bucket. The [`terraform init`](https://www.terraform.io/docs/commands/init.html) command is also run which pulls down any [Terraform modules](https://www.terraform.io/docs/modules/index.html) referenced in the Terraform code and any required [provider plugins](https://www.terraform.io/docs/providers/index.html).

All of these dependencies plus metadata about this version of the release, including references to the built artifacts, is stored in a zip file and published to an S3 bucket. When the `cdflow deploy` command is run the tool finds the zip archive it needs in S3, downloads and unzips it and then runs [`terraform apply`](https://www.terraform.io/docs/commands/apply.html) against the infrastructure code. It is this step that creates or updates the infrastructure and performs the deployment of the artifact built during the _release_ phase.

![cdflow overview](/assets/cdflow.svg)

## Contributing

Contributions are welcome; we encourage you raise issues and pull requests to help us make CDFlow better.

For pull requests, we require a tests to replicate your issue or feature and to follow our style guide. We use PEP 8 style for Python and have a linter that should display any issues. You can run the tests with the `/test.sh` script in the root of both the [cdflow](https://github.com/mergermarket/cdflow) and [cdflow-commands](https://github.com/mergermarket/cdflow-commands) when making changes.
