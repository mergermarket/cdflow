---
title: Getting Started
menu: cdflow
weight: 1
---

# Getting Started

Here you will find all of the steps to get started using cdflow in your project.

# Installing

To install the `cdflow` tool, put the `cdflow.py` script somewhere on your `PATH` and make it executable e.g.

```bash
curl -o /usr/local/bin/cdflow https://raw.githubusercontent.com/mergermarket/cdflow/master/cdflow.py
```

## Prerequisites

To use the `cdflow` tool you'll need:

 - Docker (https://docs.docker.com/engine/installation/)
 - Python
 - Python packages (`pip install -U docker boto3 PyYAML`)

## Verifying Installation

You can verify cdflow is installed correctly by opening a new terminal session and trying `cdflow`. By executing 'help' you should see helpful output like below

```
$ cdflow --help

cdflow

Create and manage software services using continuous delivery.

Usage:
    cdflow release (--platform-config <platform_config>)... <version> [options]
    cdflow deploy <environment> <version> [options]
    cdflow destroy <environment> [options]

Options:
    -c <component_name>, --component <component_name>
    -v, --verbose
    -p, --plan-only
```

# Runtime Requirements

The tool requires some additional components to be able to build and deploy releases.

## Account Scheme

To work out where to store releases and which account corresponds to which environment `cdflow` uses an account scheme. This is a JSON file which needs to be stored in an S3 bucket in an AWS account and the IAM user running the `cdflow` command needs to be able to access that S3 URL.

The URL is included in the `cdflow.yml` file under the `account-scheme-url` key.

See the [account-scheme.json reference](reference/account-scheme-json.md).


## Platform Config

This defines information about common resources that are needed by components being deployed e.g. VPC, subnets etc. It's passed as a JSON file to the Terraform and the map is then accessible within the Terraform code.
