---
title: account-scheme.json
menu: reference
weight: 1
---

{% include notice.html %}

# account-scheme.json Reference

These are the list of properties you can have in the account scheme json file. This file should be named `account-scheme.json` and exist in an s3 bucket.


| Key | Default | Required | Description | Example |
| --- | ------- | -------- | ----------- | ------- |
|`accounts` | - | yes | A json object representing an AWS account and the role to assume whilst making changes i.e. deploying | `"account_alias":{ "id": "1234567890", "role": "admin" }` |
|`release-account` | - | yes | The account where the ECR docker images are stored | `"account_alias"` |
|`release-bucket` | - | yes | The s3 bucket where terraform state files should be stored | `"some-bucket-name"` |
|`environments`| - | yes | Which accounts map to which environment when you run a deploy | `"*": "account_alias"` |
|`default-region`| - | yes | If region isn't in the environment, which AWS region resources should be deployed to | `"eu-west-1"` | 
|`ecr-registry` | - | yes | The ECR Registry where the docker images are stored | `"1234567890.dkr.ecr.eu-west-1.amazonaws.com"`| 
|`lambda-bucket` | - | yes | The s3 bucket where lambda functions are pushed to and stored| `"some-bucket-name"` | 

Quick Example:
```
{
  "accounts": {
    "some_alias": {
      "id": "1234567890",
      "role": "admin"
    }
  },
  "release-account": "some_alias",
  "release-bucket": "some-bucket-name",
  "environments": {
    "*": "some_alias"
  },
  "default-region": "eu-west-1",
  "ecr-registry": "1234567980.dkr.ecr.eu-west-1.amazonaws.com",
  "lambda-bucket": "some-other-bucket-name"
}
```