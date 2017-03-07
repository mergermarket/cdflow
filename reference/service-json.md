---
title: service.json
menu: reference
weight: 1
---

# service.json reference

`service.json` is a metadata file you place in the root of your repository
containing metdata about your service.

| Key | Default | Required | Description | Example |
| --- | ------- | -------- | ----------- | ------- |
| `TEAM` | - | yes | The name of the team that maintains the service. | `the-a-team` |
| `TYPE` | - | yes | The type of project. | `docker` |
| `ACCOUNT_PREFIX` | - | yes | Prefix on AWS acccount names, with "dev" and "prod" appended. | `mmg` |
| `REGION` | - | yes | The region the service is deployed to. | `eu-west-1` |
| `ECS_CLUSTER` | `default` | no | The ECS cluster that the service should run on. | `testing` |  
