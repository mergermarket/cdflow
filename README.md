# Mergermarket infrastructure scripts

These infrastructure scripts are provided to help deploy your service. The latest version of the documentation can be found at [mergermarket.github.io/infra](https://mergermarket.github.io/infra/) (built from [docs/](docs/)).

This repository contains scripts provided by the [Mergermarket Platform Team](mailto:platform@mergermarket.com) for building and deploying services. This guide contains an overview of the structure of the project, as well as instructions for using in your services. It is designed to be as unspecific to Mergermarket as possible (deployment scripts not being our core business) - where instructions are specific they will be indicated as such.

## Structure

The module is intended to be included directly in your service repository under the `infra/` folder - see [Usage in your repository](#usage-in-your-repository) below.

## Usage in your repository

This repository contains a single `infra/` folder. It's intended to be merged into your project as follows:

### First time

    git pull --allow-unrelated-histories git@github.com:mergermarket/infra.git master
    
    # or
    
    git pull --allow-unrelated-histories https://github.com/mergermarket/infra.git master

Note that this will fail on older versions of git that do not support the `--allow-unrelated-histories` switch. If this is the case, just remove the flag (i.e. run one of the commands below).

### Updates

    git pull git@github.com:mergermarket/infra.git master
    
    # or
    
    git pull https://github.com/mergermarket/infra.git master

## Managing secrets in your repository
It is never a good idea (nor is justified) to store any form of sensitive credentials (passwords, keys) in plain-text form, especially commited to git.

If you need to store any secrets, @platform supports [Credstash](https://github.com/fugue/credstash) as a tool to manage secrets and use them from within Terraform (the intention is, as per 12-factor app standards - to pass any configuration and secrets as ENV variables to your container from where, your application can pull them).

In order to be able to use [Credstash](https://github.com/fugue/credstash), @platform needs to set up [KMS](https://aws.amazon.com/kms/) key for your team - if you can't confirm within your team, whether this has already been done, get in touch with @platform on #platform-team Slack channel and we'll confirm this for you, or set it up (@platform team - [this is the guide on how to do this](#setting-up-credstash-for-team)).

[Credstash](https://github.com/fugue/credstash), basically provides a simple key-value store which stores the values encrypted.  The use is simple - you store secrets using [Credstash](https://github.com/fugue/credstash) and during the deploy phase, they'll be pulled out of [Dynamo DB](https://aws.amazon.com/dynamodb/), decrypted using [KMS](https://aws.amazon.com/kms/) and presented within Terraform under `${var.secret}` map for you to use within Terraform (i.e to pass the to taskDefinition and include as ENV variable in your container).

We advise you to read on [Credstash](https://github.com/fugue/credstash) documentation on their Github repo, to get more familiar with how to use it.

### Using Credstash to manage secrets
In order to be able to use [Credstash](https://github.com/fugue/credstash), you need permission to relevant [KMS](https://aws.amazon.com/kms/) key and [Dynamo DB](https://aws.amazon.com/dynamodb/) table - both will be set up for you as a part of Credstash setup process.  

#### Conventions
For any operations, you'll need to provide a **[Dynamo DB](https://aws.amazon.com/dynamodb/) table name** (which we use as namespace) as an argument to [Credstash](https://github.com/fugue/credstash).  The convention for the table name is `credstash-%TEAMNAME%`, i.e for Team Wasabi, it'll be `credstash-wasabi`.

If you'll be putting any data into [Credstash](https://github.com/fugue/credstash), you'll also need to provide **KMS key** to be used to encrypt the data; [KMS](https://aws.amazon.com/kms/) key convention is similar to [DynamoDB](https://aws.amazon.com/dynamodb/) table naming convetion - it's `credstash-%TEAMNAME%`

Secret keys - `(deploy|runtime).%environment%.%component%.KEY_NAME`

* `(deploy|runtime)` - specifies stage at which secret should be presented; at the moment only `deploy` is supported
* `%environment%` - self explonatory
* `%component%` - self explonatory
* `KEY_NAME` - the actual key name under which the secret will be available in your Terraform configuration

#### Getting all secrets available for me to use
From your command line (make sure you installed credstash):

1) Switch to the desired role

```
$ eval $(~/dev/mmg/platform-utils/switch-aws-account csixamdev admin)
```

2) Use `credstash getall` command

```
12:12 $ credstash -t credstash-csixam getall
{
    "deploy.ci.c6-adversemedia.DB_PASS": "<REDACTED>",
    "deploy.ci.c6-adversemedia.TEST": "qwerty",
    "deploy.ci.c6-adversemedia.status": "managed"
}
```

Remember - deploy script strips there prefix of the key names, in the example above, the string `deploy.ci.c6-adversemedia.` will be stripped off the keys and keys will be available to use as `DB_PASS`, `TEST` and `status`.

#### Storing new secret
From your command line (make sure you installed credstash):

1) Switch to the desired role

```
$ eval $(~/dev/mmg/platform-utils/switch-aws-account csixamdev admin)
```

2) Use `credstash put` to put your new secret

```
12:28 $ credstash -t credstash-csixam put -k alias/credstash-csixam -a deploy.ci.c6-adversemedia.TEST "qwerty"
deploy.ci.c6-adversemedia.TEST has been stored
```

3) Confirm its there

```
12:30 $ credstash -t credstash-csixam getall
{
    "deploy.ci.c6-adversemedia.DB_PASS": "<REDACTED>",
    "deploy.ci.c6-adversemedia.TEST": "qwerty",
    "deploy.ci.c6-adversemedia.status": "managed"
}
```

### Platform configuration

The scripts depend on platform configuration - e.g. AWS accounts, VPCs, ECS clusters, etc. that the service should run on. This is specific to an organisation. If you are running a service at Mergermarket, see the instruction in [mmg-platform-config](https://github.com/mergermarket/mmg-platform-config/tree/master/infra/platform-config).

## Tests

To run the unit tests, run:

    ./infra/scripts/src/test

These are run on each push to Github by https://jenkins.mergermarket.it/job/platform/job/infra/.

## Platform setup
**NOTE** - this are mainly instructions for @platform members to follow in order to set `infra` for consumers.

### Setting up Credstash for team
In order for a team / project to be able to use Credstash, you need to create a KMS key for them as well as run `credstash -t %TABLE_NAME% setup` to pre-create Dynamo DB table.

1). Establish key and table name - `credstash-%TEAMNAME%`, so for Wasabi team it'll be `credstash-wasabi`

2). Create KMS key via console; don't grant it any admin permission, grant usage permission to user `admin`

3). Run `credstash setup` with `-t` argument to pre-create Dynamo DB table

```
13:49 $ credstash -t credstash-wasabi setup
Creating table...
Waiting for table to be created...
Table has been created. Go read the README about how to create your KMS key
```

All done!  Remember you'll need to do that per-account, i.e if you're setting team up that's running stuff in `mmgprod` and `mmgdev`, you'll need to create KMS key and Dynamo DB tables in both.
