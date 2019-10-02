# cdflow - create and manage software services using continuous delivery
[![Build Status](https://travis-ci.org/mergermarket/cdflow.svg?branch=master)](https://travis-ci.org/mergermarket/cdflow)

This repository contains the cdflow command that you can install on your system (e.g. on your dev machine or CI server) in order to release, deploy and (eventally) decommission software services with ease.

The code here is just a thin wrapper for the [cdflow docker image](https://github.com/mergermarket/cdflow-commands/) used to ensure you get the latest version when you release (with the option to pin should you need to) and that the image used remains consistent through your pipeline. 

Full documentation is here: https://mergermarket.github.io/cdflow/

## Install

```
pip install cdflow
```

## Running

If you are using the [cdflow wrapper comamnd](https://github.com/mergermarket/cdflow/) mentioned above, you can get usage information by running:

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

## Tests

```
./test.sh
```
