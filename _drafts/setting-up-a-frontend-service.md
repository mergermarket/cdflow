---
title: Setting Up A Frontend Service 
menu: guides
weight: 2
---

# Setting Up A Frontend Service

With cdflow installed, let's set up a frontend service. A frontend service is an application that is open to the public that end users can interact with. We're going this application to deploy to AWS and setup all the relevant infrastructure to have available for users to use.

# Configuration

## Project Structure

If you dont have a project ready and want to set up a quick example for testing out, have a look at this [simple service guide](simple-service-guide).

Within your project, you will need to have the following files and folders. We enforce these conventions on the project structure to make it easier for you to use a tool like Terraform and have "Infrastructure as Code" within your project.

cdflow.yml
-----------

You'll need a `cdflow.yml` file in the top-level of your project. We use this to enforce conventions on the resources created by Terraform.

Please see the [cdflow.yml reference](/reference/cdflow-yaml) for more detail.
Example below:
```yaml
account-scheme-url: s3://some-account/account-scheme.json
type: docker
team: some-team
```

config/ Folder
--------------

The `config/` folder should also exist in the top-level of your project. This folder provides configuration to your ECS service, such as the amount of memory to supply to the container, the DNS domain etc. These files are Terraform files in JSON format that are applied when a release or deploy is run.

This folder, at a minimum, should contain an `all.json` file. Please see the [all.json reference](/reference/config-all-json) for more detail.
    
`all.json`

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

You may also choose to include json files that are specific to each environment you want your service to run in.

Please see the [environment.json reference](/reference/config-env-json) for more detail.

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

infra/ Folder
-------------

The `infra/` folder should contain any Terraform files that make up your infrastructure. We provide modules that can be used to setup an ECS service. These are displayed below, using these as is should give you everything you need to deploy a service to ECS.

main.tf
```
module "ecs_service" {
  source = "github.com/mergermarket/tf_ecs_service_infrastructure"

  env                            = "${var.env}"
  platform_config                = "${var.platform_config}"
  release                        = "${var.release}"
  common_application_environment = "${var.common_application_environment}"
  application_environment        = "${var.application_environment}"
  secrets                        = "${var.secrets}"
  dns_domain                     = "${var.dns_domain}"
  ecs_cluster                    = "${var.ecs_cluster}"
  port                           = "${var.port}"
  cpu                            = "${var.cpu}"
  memory                         = "${var.memory}"
  alb_listener_arn               = "${var.alb_listener_arn}"
  alb_dns_name                   = "${var.alb_dns_name}"
  alb_listener_rule_priority     = "${var.alb_listener_rule_priority}"
}
```

variables.tf
```
variable "env" {
  description = "Environment name"
}

variable "platform_config" {
  description = "Platform configuration"
  type        = "map"
  default     = {}
}

variable "release" {
  type        = "map"
  description = "Metadata about the release"
}

variable "common_application_environment" {
  description = "Environment parameters passed to the container for all environments"
  type        = "map"
  default     = {}
}

variable "application_environment" {
  description = "Environment specific parameters passed to the container"
  type        = "map"
  default     = {}
}

variable "secrets" {
  type        = "map"
  description = "Secret credentials fetched using credstash"
  default     = {}
}

variable "dns_domain" {
  type        = "string"
  description = "The DNS domain"
}

variable "ecs_cluster" {
  type        = "string"
  description = "The ECS cluster"
  default     = "default"
}

variable "port" {
  type        = "string"
  description = "The port that container will be running on"
}

variable "cpu" {
  type        = "string"
  description = "CPU unit reservation for the container"
}

variable "memory" {
  type        = "string"
  description = "The memory reservation for the container in megabytes"
}

variable "alb_listener_arn" {
  type        = "string"
  description = "The Amazon Resource Name for the HTTPS listener on the load balancer"
}

variable "alb_dns_name" {
  type        = "string"
  description = "The DNS name of the load balancer"
}

variable "alb_listener_rule_priority" {
  type        = "string"
  description = "The priority for the rule - must be different per rule."
}

variable "desired_count" {
  description = "The number of instances of the task definition to place and keep running."
  type        = "string"
  default     = "3"
}
```
# Release

```shell
cdflow release --platform-config <platform_config> <version> [options]
```

# Deploy

```shell
cdflow deploy <environment> <version> [options]
```

# Destroy

```shell
cdflow destroy <environment> [options]
```

# Next
