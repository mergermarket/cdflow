---
title: Updating from cdflow-classic
menu: guides
weight: 5
---

# Updating from cdflow-classic 

We have updated the implementation of cdflow and made some changes to the project that you will have to apply to your repository.

## Step-by-step

1. You'll need the `infra` folder in your repo with the new `.tf` files.
   You can copy the files from the [node-minimal-boilerplate](https://github.com/mergermarket/node-minimal-boilerplate/tree/master/infra) repo.

2. Add a `cdflow.yml` file. 
Please see the [cdflow.yml reference](/reference/cdflow-yaml) for more detail.
Example below:
```yaml
account-scheme-url: s3://resources/accounts.json
type: docker
team: DevTeam-Platform
```
3. Update the `Jenkinsfile` to use `cdflow` from PATH

4. Update the config files. 
Please see the [all.json reference](/reference/config-all-json) for more detail.
    
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
