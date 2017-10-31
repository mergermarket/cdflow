---
title: cdflow.yml
menu: reference
weight: 30
---

# cdflow.yml Reference

These are the list of properties you can have in the cdflow manifest file. This file should be named `cdflow.yml` in your project.


| Key | Default | Required | Description | Example |
| --- | ------- | -------- | ----------- | ------- |
| `account-scheme-url` | - | yes | The account scheme url should point to an s3 bucket that contains the account information, in json format, for the account(s) you wish to deploy to. | `s3://mmg-account-resources/account-scheme.json` |
| `type` | - | yes | The type of project. | `docker`, `infrastructure`, `lambda` |
| `team` | - | yes | Your team name. | `platform` |

## Quick Example

```yaml
    account-scheme-url: s3://mmg-account-resources/account-scheme.json
    type: docker
    team: DevTeam-Platform
```
