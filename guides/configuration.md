---
title: Configuration
menu: guides
weight: 3
---

# Configuration

This guide describes how to add environment specific configuration to your service repository that will be provided to your container(s) within an environment as environment variables. Since this configuration is stored with the code in your service repository, changes require that your code is redeployed - i.e. it is not suitable for configuration that needs to be dynamically updated without a redeploy. Also, since configuration is stored in the repository in plain text, it is not suitable for storing secrets or credentials - if you need that see the [managing secrets](secrets/) guide.

## TL;DR

Place your config in `config/ENV.json`:

```json
{
  "container_env": {
    "MY_CONFIG_VAR": "my-config-value"
  }
}
```

In addition to this, there are two places where we need to pass this through in order to expose it to your container:

### `infra/main.tf`

```terraform
data "template_file" "container_definitions" {
    ...
    vars {
       ...
       # Add a line like the following (there should be a commented example):
       MY_CONFIG_VAR   = "${var.container_env["MY_CONFIG_VAR"]}"
       ...
    }
}
```

### `infra/container_definitions.json`

```terraform
[
  {
    ...
    "environment": [
      ...
      { "name": "MY_CONFIG_VAR", "value": "${MY_CONFIG_VAR}" }
    ],
    ...
  }
]   
```

Read on for a more long-winded description of this configuration.

## Adding environment specific config to Terraform

If there is a file called `config/ENVIRONMENT_NAME.json` (e.g. `config/aslive.json`) committed to your repository, then it will be used as a Terraform `-var-file` for input variables.

Deployment to a given environment is triggered via the following (hopefully from within a Jenkins pipeline):

```Shell
infra/scripts/deploy ENVIRONMENT_NAME VERSION
```

For example, deploying version `7` to `aslive` would be triggered with:

```Shell
infra/scripts/deploy aslive 7
```

By default, this will result in [Terraform](https://www.terraform.io/) being triggered (via [Terragrunt](https://github.com/gruntwork-io/terragrunt)) simliar to the following (as it appears in the output):

```
[terragrunt] 2017/01/01 00:00:00 Running command: \
  terraform apply \
  -var env=aslive \
  ...
  -var version="7" \
  -var-file infra/platform-config/mmg/dev/eu-west-1.json \
  infra
```

If there exists a file `config/ENVIRONMENT_NAME.json` (e.g. `config/aslive.json`), then an additional `-var-file` will be added to include this file:

```
[terragrunt] 2017/01/01 00:00:00 Running command: \
  terraform apply \
  -var env=aslive \
  ...
  -var version="7" \
  -var-file infra/platform-config/mmg/dev/eu-west-1.json \
  -var-file config/aslive.json \
  infra
```

## Config format

The `config/ENVIRONMENT_NAME.json` file is a JSON file containing the values for any input parameters defined in your Terraform code (i.e. the `.tf` files under `infra/` - by convention in `infra/params.tf`). The default inlcudes a parameter called `container_env`:

```terraform
variable "container_env" {
  description = "Environment parameters passed to the container"
  type        = "map"
  default     = {}
}
```

Since this input variable is defined as a map, you can add it with any keys you want in your config file:

### config/aslive.json

```json
{
  "container_env": {
    "MY_CONFIG_VAR": "my aslive config value"
  }
}
```

## Providing config values to your containers

The above will provide a value within the `container_env` map to your Terraform code when deploying to `aslive`. However, by default nothing within the Terraform code will use this. To expose this value to your container, you will need to change the way your [ECS task definition](http://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_defintions.html) is generated to include the value.

### infra/main.tf

Within the `infra/main.tf` file, the following block controls rendering the ECS task definition:

```terraform
data "template_file" "container_definitions" {
  template = "${file("${path.module}/container_definitions.json")}"
  
  vars {
    # place your config environment variables here to make the available to your
    # container definitions template, for example:
    # MY_CONFIG_VAR   = "${var.container_env["MY_CONFIG_VAR"]}"

    # standard variables
    ...
  }
}
```

To pass a value from the `container_env` map to the template, add a line similar to the example from the comment:

```terraform
data "template_file" "container_definitions" {
  template = "${file("${path.module}/container_definitions.json")}"
  
  vars {
    # place your config environment variables here to make the available to your
    # container definitions template, for example:
    # MY_CONFIG_VAR   = "${var.container_env["MY_CONFIG_VAR"]}"
    
    MY_CONFIG_VAR   = "${var.container_env["MY_CONFIG_VAR"]}"

    # standard variables
    ...
  }
}
```

### infra/container_definitions.json

Finally, the template itself is contained in the file `infra/container_definitions.json`. To add the value to the container's environment, pass the provided value in the `environment`:

```json
[
  {
    ...
    "environment": [
       ...
       { "name": "MY_CONFIG_VAR", "value": "${MY_CONFIG_VAR}" }
    ]
    ...
  }
]
```
