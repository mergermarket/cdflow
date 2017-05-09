---
title: Using Lambda Module
menu: guides
weight: 3
---

# Using Lambda Module

## Directory structure

All of your code for the lambda **(including dependencies)** will need to be in a directory that is the same name as the component name.
The component name is generated at runtime either by the name of the git repo _or_ can be passed through as a command line argument when running:
```shell
./infra/scripts/cdflow release 1 --component cool-name
```
So the structure should look something like this:
```
cool-name
├── Jenkinsfile
├── README.md
├── cool-name
│   ├── __init__.py
│   ├── simple_lambda.py
├── config
│   ├── README.md
│   └── live.json.example
├── infra
│   ├── modules
│   │   └── lambda
│   │       ├── iam.tf
│   │       ├── main.tf
│   │       ├── sg.tf
│   │       └── variables.tf
│   ├── platform-config
│   │   ├── mmg
│   │   │   ├── dev
│   │   │   │   └── eu-west-1.json
│   ├── scripts
│   │   ├── README.md
│   │   └── cdflow
└── service.json
```

## service.json

You'll need to add a `service.json` file to the top level of your repo that specifies `"lambda"` as the project `"TYPE"`. 

You will need to specify the `"HANDLER"`. AWS documentation on the Lambda handler method can be found [here](http://docs.aws.amazon.com/lambda/latest/dg/programming-model-v2.html).

And also specify the `"RUNTIME"`. Docs on which runtime can be run using Lambda are [here](http://docs.aws.amazon.com/lambda/latest/dg/lambda-app.html). Allowed values are from the boto client library specified [here](http://boto3.readthedocs.io/en/latest/reference/services/lambda.html#Lambda.Client.create_function).

```json
{
  "TEAM": "platform",
  "TYPE": "lambda",
  "REGION": "eu-west-1",
  "ACCOUNT_PREFIX": "mmg",
  "HANDLER": "cool-name.simple_lambda.my_handler",
  "RUNTIME": "python3.6"
}
```
## Running
### Release
Once you run:
```shell
./infra/scripts/cdflow release <version>
```
This should zip up the contents of the directory the the same name as your component and send it to a bucket in s3. With the key `{team-name}/{component}/{version}.zip`.
### Deploy
Running:
```shell
./infra/scripts/cdflow deploy <environement> <version>
```
Will create a lambda function in AWS.