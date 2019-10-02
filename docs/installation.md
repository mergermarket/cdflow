---
menu: docs
weight: 5
---

## Prerequisites

To use the `cdflow` tool you'll need:

 - Docker (https://docs.docker.com/engine/installation/)
 - Python and `pip`

# Installation

Use the `pip` command to install CDFlow:

```bash
pip install cdflow
```

You may need to prefix the command with `sudo`, or install it in your user directory:

```shell
pip install --user cdflow
```

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

