---
menu: docs
weight: 30
---

# cdflow deploy

`cdflow deploy <environment> <version> [options]`

The `deploy` command performs a `terraform plan` and (unless `--plan-only` is passed) `terraform apply` on a bundle created with a `<version>` during [`cdflow release`](cdflow-release). This creates or updates any virtual infrastructure defined by the code in the `infra` directory.

Before running `terraform plan`, `cdflow` will set up remote state and locking in S3 and DynamoDB with values for the bucket and table taken from values in the [account scheme]({{ site.baseurl }}{% link reference/account-scheme-json.md %}).
