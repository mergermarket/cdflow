---
title: Configuration
menu: guides
weight: 99
---

# Service Configuration

### TL;DR

Place your config in `config/ENV.json`:

```json
{
  "application_environment": {
    "MY_CONFIG_VAR": "my-config-value"
  }
}
```

## Common Service Configuration

Configuration files for your service should be placed in the `config/` directory in `.json` format.

Common service configuration should be placed in a `common.json` file. This file contains the common properties of your service across all environments. Such as CPU, Memory allocation, DNS domain.

Environment variables that are exposed to your service, which have the same value across all environments can be specified here (`common_application_environment`) so as not to duplicate in each environment file.

### Quick Example
`common.json`
```json
{
    "dns_domain": "example.com",
    "cpu": 16,
    "memory": 128,
    "port": 8000,
    "alb_listener_rule_priority": 100,
    "common_application_environment": {
        "ENV_VAR": "value"
    }
}
```

A full reference to the `common.json` file can be found [here](/reference/config-all-json).

## Environment Specific Service Configuration

Configuration files for your service should be placed in the `config/` directory in `.json` format.

Environment specific configuration should be placed in a `.json` file. The file name should match the environment that you are deploying to i.e the first argument you pass to the `cdflow deploy` command.

### Quick Example

`environment.json`
```json
{
    "application_environment": {
        "ANOTHER_ENV_VAR": "value"
    },
    "alb_listener_arn": "arn:aws:...",
    "alb_dns_name": "...elb.amazonaws.com"
}
```

A full reference to the `environment.json` file can be found [here](/reference/config-env-json).

## Secret Service Configuration

As configuration is stored in the repository in plain text, it is not suitable for storing secrets or credentials - if you need that see the [managing secrets](secrets/) guide.

In addition to this, there are two places where we need to pass this through in order to expose it to your container:

# Working with Terraform

## Terraform Service Configuration Variables 

A cdflow service requires **all** the input parameters that are defined in the `infra/params.tf` file.
Any parameters specified in the `infra/params.tf` which **do not have a default** must be passed in. If a parameter does not exist in anywhere in the `config/` directory and has no default the deployment will throw an error.

All `.json` files in the `config/` directory are passed to Terraform as a `-var-file`. You can find more info in the Terraform docs [here](https://www.terraform.io/intro/getting-started/variables.html#from-a-file). 

### Quick Example

Example parameter from `infra/params.tf`
```terraform
variable "application_environment" {
  description = "Environment parameters passed to the container"
  type        = "map"
  default     = {}
}
```

Passed through as config `config/aslive.json`

```json
{
  "application_environment": {
    "MY_CONFIG_VAR": "my aslive config value"
  }
}
```
Since this input variable (`params.tf`) is defined as a map (`type = "map"`), you can add it with any keys you want in your config file (`aslive.json`).
