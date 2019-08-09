---
title: cdflow(1)
author:
  - Graham Lyons
  - Arthur Gassner
  - Keir Badger
  - Tom Yandell
date:  July 2019
section: 1
---

# NAME

**cdflow** - create and manage software services using continuous delivery

# SYNOPSIS

| **cdflow release** **\--platform-config** _platform\_config_... _version_ [_options_]
| **cdflow deploy** _environment_ _version_ [_options_]
| **cdflow destroy** _environment_ [_options_]
| **cdflow shell** _environment_

# DESCRIPTION

**cdflow** is a program to create and manage services in a continuous delivery
pipeline using **terraform**. The intended workflow is to generate an artifact
using **cdflow release**, which is then deployed to one or more environments
using **cdflow deploy**.

## Environment

**cdflow** expects to be run from the root of a project. It assumes that there to be the following files in its environment:

- _cdflow.yml_, a yaml file with the following fields:
    - _team_: the name of your team.
    - _account_scheme_: provided by your platform team.
    - _type_: one of either _docker_, _lambda_, or _infra_.

- an _infra_ folder containing valid **terraform** config files.

- an optional _config_ folder, containing JSON **terraform** variable files.


## cdflow release

Builds and publishes a release. The information in the release allows **cdflow
deploy** to run **terraform** in a repeatable way, in an attempt to produce
identical deployments each time. This information is stored in an AWS S3 bucket.

Always included are

  - platform configuration
  - component configuration (the _config_ folder, see above)
  - **cdflow** version
  - **terraform** version
  - **terraform** providers and modules (from the _infra_ folder, see above).

An additional artefact will be produced, based upon the based upon the _type_ field in the _cdflow.yml_ file (see above):

- _docker_

    A Docker image created from a _Dockerfile_ in the root of the
    project. This image is also published to an AWS [Elastic Container Registry][ecr].

- _lambda_

    A zip file of the project's _src_ folder, suitable for deployment as an AWS
    lambda. This zip file is also published to a separate AWS S3 bucket.

- _infra_

    No extra artefacts will be produced.

The _version_ parameter is the user-defined identfier for the release. It must
be unique. Conventionally this will be the build number, a hyphen, and then the
short **git** commit identifier.

## cdflow deploy

Deploys the artefact created with **cdflow release** to the specified
_environment_. The _environment_ describes a named set of services that work
together. The deployment will change, create or remove infrastructure in that
environment.

Conventionally there is always an environment called _live_, where end
users will interact with your service. Other environments may be available
(i.e. _ci_, _aslive_, etc...).

**--plan-only** or **-p** will describe the changes that would be made to the
infrastructure of that environment without actually making them.

## cdflow destroy

Removes the infrastructure associated with a project from the specified _environment_.

## cdflow shell

describe shell command and what it does

# OPTIONS

**-c** _component\_name_, **--component** _component\_name_
: something to do with a component name

**-v**, **--verbose**
: Give verbose logging output

**-p**, **--plan-only**
: Generate and show terraform execution plan. Only for **cdflow deploy**.

# SEE ALSO

- [terraform](https://www.terraform.io)
- [Elastic Container Registry][ecr]
- [AWS](https://aws.amazon.com)

[ecr]: https://aws.amazon.com/ecr/
