---
menu: docs
weight: 5
---

# Installation

To install the `cdflow` tool, put the `cdflow.py` script somewhere on your `PATH` and make it executable e.g.

```bash
curl -o /usr/local/bin/cdflow https://raw.githubusercontent.com/mergermarket/cdflow/master/cdflow.py
```

A `man` page is also available

```bash
curl -o /usr/local/share/man/man1/cdflow.1 https://raw.githubusercontent.com/mergermarket/cdflow/master/docs/cdflow.1
```

## Prerequisites

To use the `cdflow` tool you'll need:

 - Docker (https://docs.docker.com/engine/installation/)
 - Python
 - Python packages (`pip install -U docker boto3 PyYAML dockerpty`)

## Verifying Installation

You can verify cdflow is installed correctly by opening a new terminal session and trying `cdflow`. By executing 'help' you should see helpful output like below

```
$ cdflow --help

cdflow

Create and manage software services using continuous delivery.

Usage:
    cdflow release (--platform-config <platform_config>)...
                   [--release-data=key=value]... <version> [options]
    cdflow deploy <environment> <version> [options]
    cdflow destroy <environment> [options]
    cdflow shell <environment> [<version>] [options]

Options:
    -c <component_name>, --component <component_name>
    -v, --verbose
    -p, --plan-only
```

