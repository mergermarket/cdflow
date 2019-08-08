---
menu: reference
weight: 50
---

# \<environment\>.json

This is a file containing variables passed to `terraform`, when `cdflow deploy` is called, as a `-var-file`. The name of the file will be determined by the name of the environment being deployed to. For example, calling `cdflow deploy live <version>` will pass the `./config/live.json` file to Terraform, e.g. `terraform plan -var-file config/live.json ...`. Each of the top level keys in the file must be defined in a `variable` block in the `./infra/*.tf` files.

## Example

`./config/live.json`:
```json
    {
        "static_assets_url": "https://cdn.example.com/",
        "application_environment": {
            "ENV_VAR": "value"
        }
    }
```

`./infra/variables.tf`:
```hcl
variable "static_assets_url" {
  type        = "string"
  description = "The base url to serve static files from"
}

variable "application_environment" {
  type        = "map"
  description = "A map of environment variables to be passed to the service"
}
```
