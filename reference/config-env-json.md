---
menu: reference
weight: 50
---

# \<environment\>.json

{% include notice.html %}

These are the list of properties you can have in an environment config file like `aslive.json` or `live.json` which should exist in the `config/` directory of your project.


| Key | Default | Required | Description | Example |
| --- | ------- | -------- | ----------- | ------- |
| `alb_dns_name` | - | no | The dns name for the application load balancer that your service will belong to| `internal-aslive-platform-mergermarket-it-1234.eu-west-1.elb.amazonaws.com` |
| `alb_listener_arn` | - | no | The arn of the application load balancer that your service will belong to| `arn:aws:elasticloadbalancing:eu-west-1:123456:listener/app/aslive-platform-mergermarket-it/123abc/123abc` |
| `application_environment` | - | no (can be empty) | Environment variables you want exposed to your service for that particular environment | `{ "VERSION" : "123" }` |

## Quick Example

```json
    {
        "application_environment": {
            "ANOTHER_ENV_VAR": "value"
        },
        "alb_listener_arn": "arn:aws:...",
        "alb_dns_name": "...elb.amazonaws.com"
    }
```
