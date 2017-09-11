---
title: Getting Started
menu: cdflow
weight: 1
---

# Getting Started

Here you will find all of the steps to get started using cdflow in your project.

# Installing cdflow

To Install cdflow clone the cdflow repo from [here](https://github.com/mergermarket/cdflow), and copy the `cdflow.py` file into your PATH.
```
cp cdflow.py /usr/local/bin/cdflow
```

# Verifying Installation

You can verify cdflow is installed correctly by opening a new terminal session and trying `cdflow`. By executing 'help' you should see helpful output like below

```
$ cdflow --help

cdflow

Create and manage software services using continuous delivery.

Usage:
    cdflow release --platform-config <platform_config> <version> [options]
    cdflow deploy <environment> <version> [options]
    cdflow destroy <environment> [options]

Options:
    -c <component_name>, --component <component_name>
    -v, --verbose
    -p, --plan-only
```

# cdflow Prerequisites

Once cdflow is installed, you'll need to setup some resources that you will use when using cdflow.

Account Scheme
--------------

For the docs, go [here](/full-documentation/account-scheme)

External Config
---------------

For the docs, go [here](/full-documentation/platform-config).

Application Load Balancer
-------------------------

For the docs, go [here](/full-documentation/ALB).

# Next

See how to use cdflow to deploy a [frontend service](setting-up-a-frontend-service), [backend service](setting-up-a-backend-service), [lambda function](setting-up-a-lambda-function), or [infrastructure](setting-up-infrastructure).