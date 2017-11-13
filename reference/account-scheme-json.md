---
menu: reference
weight: 10
---

# account-scheme.json

These are the list of properties you can have in the account scheme json file. This file should be stored in an S3 bucket under a key which is accessible to the IAM user running the `cdflow` tools.


| Key | Default | Required | Description | Example |
| --- | ------- | -------- | ----------- | ------- |
|`accounts` | - | yes | A json object representing an AWS account and the role to assume whilst making changes i.e. deploying | `"account_alias":{ "id": "1234567890", "role": "admin" }` |
|`release-account` | - | yes | The alias of the account where the built artefacts e.g. docker images, are stored | `"account_alias"` |
|`release-bucket` | - | yes | The S3 bucket where release artefacts are stored, in the `release-account` | `"some-bucket-name"` |
|`environments`| - | yes | Which accounts map to which environment when you run a deploy | `"*": "account_alias"` |
|`default-region`| - | yes | If region isn't in the environment, which AWS region resources should be deployed to | `"eu-west-1"` | 

Quick Example:
```
{
  "accounts": {
    "dev": {
      "id": "1234567890",
      "role": "admin"
    },
    "prod": {
      "id": "0987654321",
      "role": "admin"
    }
  },
  "release-account": "dev",
  "release-bucket": "org-releases",
  "environments": {
    "live": "prod",
    "*": "dev"
  },
  "default-region": "eu-west-1"
}
```
