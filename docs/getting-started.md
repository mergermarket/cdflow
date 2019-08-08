---
menu: docs
weight: 10
---

# Getting Started

Here you will find all of the steps to get started using cdflow in your project.

## Runtime Requirements

The tool requires some additional components to be able to build and deploy releases.

### cdflow.yml
The project must have a [`cdflow.yml`]({{ site.baseurl }}{% link reference/cdflow-yaml.md %}) file in its root. This has information about the type of project, the team who owns it and the account scheme to tell `cdflow` about which AWS accounts it should use for deployment.

See the [cdflow.yml reference]({{ site.baseurl }}{% link reference/cdflow-yaml.md %}).

### Account Scheme

To work out where to store releases and which account corresponds to which environment `cdflow` uses an account scheme. This is a JSON file which needs to be stored in an S3 bucket in an AWS account and the IAM user running the `cdflow` command needs to be able to access that S3 URL.

The URL is included in the [`cdflow.yml`]({{ site.baseurl }}{% link reference/cdflow-yaml.md %}) file under the `account-scheme-url` key.

See the [account-scheme.json reference]({{ site.baseurl }}{% link reference/account-scheme-json.md %}).


### Platform Config

This defines information about common resources that are needed by components being deployed e.g. VPC, subnets etc. It's passed as a JSON file to the Terraform and the map is then accessible within the Terraform code.

See the [Platform config reference]({{ site.baseurl }}{% link reference/platform-config-json.md %}).
