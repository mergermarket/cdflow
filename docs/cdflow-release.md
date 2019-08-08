---
menu: docs
weight: 20
---

# cdflow release

`cdflow release (--platform-config <platform_config>)... [--release-data=key=value]... <version> [options]`

The `release` command builds a release bundle which can then be deployed - it's required to run the `release` command before being able to run `deploy`. The `release` command requires a version and may require a `--platform-config` directory. Other values can be passed using `--release-data` flags.

Running `release` will cause `terraform init` to be run against the `infra` directory of your project. Terraform will then download any providers and modules it needs to run your infrastructure code.

For some project types `cdflow release` will perform a build, then it will initialise Terraform to pull in its dependencies, finally it will create a zip archive of everything required to perform a deployment:
- details of the artifact created during the build (if it was run)
- other information relating to the release such as the name of the project, the team name, the version
- the platform config, local config
- and the Terraform code and its dependencies.

The zip archive is stored in S3 and downloaded during [`cdflow deploy`](cdflow-deploy).
