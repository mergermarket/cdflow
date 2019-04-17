---
menu: docs
weight: 50
---

# cdflow shell

`cdflow shell <environment> [<version>] [--verbose]`

The `shell` command puts you into a bash session with Terraform correctly initialised and pointing to the remote state location configured in the account scheme. This allows for more rapid iterative development on the Terraform code.

The local component directory is mounted inside the `cdflow-commands` container and the session starts in the `./infra` folder.

It is recommended to use the command with the optional release version argument, in which case the release bundle is downloaded and Terraform is initialised with the providers within it. The platform config and release metadata from the release bundle are copied into the `./infra` folder and a `plan.sh` script is generated which can be used to plan changes. The plan can then be applied with `terraform apply`.

## plan.sh

The `plan.sh` script contains a `terraform plan` command and passes all the required `-var-file` and `-var` flags which are handled by `cdflow` during a `deploy` command. It will generate a plan file named `plan-<timestamp>` which can then be applied with `terraform apply plan-<timestamp>`.

## Environment

The bash session is within an [Alpine Linux](https://wiki.alpinelinux.org/wiki/Main_Page) container so packages can be installed with `apk add`, should they be required.
