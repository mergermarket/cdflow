---
menu: reference
weight: 40
---

# common.json

This is a file containing variables passed to `terraform`, when `cdflow deploy` is called, as a `-var-file` i.e. `terraform plan -var-file config/common.json ...`. Each of the top level keys in the file must be defined in a `variable` block in the `./infra/*.tf` files.

## Example

`./config/common.json`:
```json
    {
        "cpu": 16,
        "memory": 128,
        "common_application_environment": {
            "ENV_VAR": "value"
        }
    }
```

`./infra/variables.tf`:
```hcl
variable "cpu" {
  type        = "string"
  description = "The amount of CPU assigned to the service"
}

variable "memory" {
  type        = "string"
  description = "The amount of memory assigned to the service"
}

variable "common_application_environment" {
  type        = "map"
  description = "A map of environment variables to be passed to the service"
}
```
