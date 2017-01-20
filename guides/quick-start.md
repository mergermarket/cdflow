---
title: Quick start guide
menu: guides
weight: 1
---

# Mergermarket infra quick start

This guide will cover how to set up a new service based on the Mergermarket infra scripts quickly if you are working at Mergermarket - it uses a service to create a repo in the [mergermarket Github organisation](https://github.com/mergermarket/) and job in Mergermarket's Jenkins instnace, so won't work outside of Mergermarket. The steps are the same as those described in the [Manual Setup guide](./manual-setup).

## Pre-requisites

In order to create a service, you will need:

* A team folder in Jenkins and a corresponding team group in Github. If this is a new team, or if you need further guidance ask *@platform* in [#platform-team channel in mergermarket slack](https://mergermarket.slack.com/messages/platform-team/).
* A boilerplate project to start with - try searching the [mergermarket Github organisation](https://github.com/mergermarket/) for repositories with "boilerplate" in the name (check the README too).

## Create initial service

From the root of your workspace (i.e. where you check projects out to) run the following command, substituting in the name of your new service, the boilerplate and team:

    curl -fsS https://setup.mergermarket.it/setup.sh | sh -s -- \
        --name <name-of-your-service> \
        --boilerplate <boilerplate-repo> \
        --team <your-team>

Note: if you are uncomfortable with downloading and running this script in a single step, it's also fine to download it and inspect it before running it.

Replace each of the parameter values as described:

* *\<name-of-your-service>* - should be lower-case with words separated by hyphens (i.e. "kebab-case"). The Mergermarket convention is to end services that are used by staff with "-admin", to end services used by subscribers with "-subscriber" and to end backend services with "-service".
* *\<boilerplate-repo>* - the full git url starting "git@github.com:" or "https://github.com/" -  the protocol you chose here will be used to pull from the boilerplate, as well as to pull in platform config and to configure the remote that will be used for the service repo itself.
* *\<your-team>* - the name of the team exactly as it appears in Jenkins (check the URL in case there is an alias configured) and in the Github team.

If the script completes successfully, you should now have the following:

* A repo in Github including the code from the boilerplate, cloned in your workspace.
* Platform configuration added to your project under `infra/platform-config` (see `infra/platform-config/README.md` for instructions on how to update this in the future).
* A Jenkins pipeline in your team's jenkins folder.

The Jenkins pipeline is configured to trigger every time a change is pushed to Github. However this only happens are the initial run, so the first time you will have to trigger it manually. You will most likely need to perform some customisation first though...

## Customisation

By default the `infra/` folder will contain what's needed for a basic ECS service. This section describes common customisations to this. This is the default [infra](https://github.com/mergermarket/infra) default, but can be customised/changed by a given boilerplate - if this is the case, then refer to the documentation for that boilerplate for how to perform customisations instead.

### `TEAM` in `service.json`

This is used to tag the infrastructure for your service, to make it easy to find in monitoring, logging, billing, etc. It should be set to the same as what you provided when you created the initial service (we have automation planned for this).

### `ACCOUNT_PREFIX` in `service.json` (optional)

Mergermarket runs multiple AWS accounts. Accounts are created in pairs, one containing non-production infrastructure with the "dev" postfix (e.g. "mmgdev") and one containing production infrastructure with the "prod" postfix (e.g. "mmgprod"). The other part of the name (i.e. "mmg" in this example) is the _account prefix_ (with default "mmg"). Whatever account you use, there should be a corresponding subfolder inside `infra/platform-config/`.

### `REGION` in `service.json` (optional)

This determines the AWS region your service will run in (default `eu-west-1`). Before picking a region, you should make sure the platform has infrastructure available there, configured in `infra/platform-config/ACCOUNT_PREFIX/REGION`.

### Terraform customisation

The above should be enough to execute [Terraform](https://www.terraform.io/), which is used to provision infrastructure. Any further customisations will be in the Terraform config inside `infra/`.

#### DNS name for your service

By default your service will have a dedicated [Application Load Balancer](https://aws.amazon.com/elasticloadbalancing/applicationloadbalancer/), with a DNS name under the `mmgapi.net` domain (this will only work in the mmgprod/mmgdev accounts as that is where the `mmgapi.net` and `dev.mmgapi.net` DNS zones are hosted).

If you are using the mmgprod/mmgdev accounts (i.e. "mmg" account prefix) in `eu-west-1`, the domains available are:

* `mmgapi.net` - used for backend services, which by convention have the `-service` postfix in the component name (removed when used in the domain - e.g. `company-search-service` becomes `company-search.mmgapi.net`).
* `mmgsubscriber.com` - used for subscriber facing services, which by convention have the `-subscriber` postfix in the component name (removed when used in the domain - e.g. `intel-viewer-subscriber` becomes `intel-viewer.mmgsubscriber.com`). However, subscriber facing services are more likely to need to add routes into an existing subscriber facing ALB - see below.
* `mmgadmin.com` - used for services used by internal users, which by convention have the `-admin` postfix in the component name (removed when used in the domain - e.g. `companies-admin` becomes `companies.mmgadmin.com`).
* `mergermarket.it` - used for tools used by the Mergermarket IT team.

For other accounts and regions, see the config keys prefixed with `route53_zone_id.` in `infra/platform-config/ACCOUNT_PREFIX/dev|prod/REGION.json`.

#### Using an existing ALB

Subscriber facing micro-services may not need their own Application Load Balancer and domain name, but instead may just expose some URLs as part of a larger product. To do this, follow the [adding routes to an existing load balancer](adding-routes-to-an-existing-alb) guide.

## Next steps

* Find out more about the process of setting up a project in the [manual setup guide](manual-setup).
* [Service configuration guide](configuration).

