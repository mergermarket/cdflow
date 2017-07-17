---
title: Quick start guide
menu: guides
weight: 1
---

# cdflow quick start

This guide will cover how to quickly set up a new service using cdflow _**if**_ you are working with Mergermarket - it uses a service to create a repo in the [mergermarket Github organisation](https://github.com/mergermarket/) and job in Mergermarket's Jenkins instance, so won't work outside of Mergermarket. The steps are the same as those described in the [Manual Setup guide](./manual-setup).

## Pre-requisites

In order to create a service, you will need:

* A team folder in Jenkins and a corresponding team group in Github. If this is a new team, or if you need further guidance ask *@platform* in [#platform-team](https://mergermarket.slack.com/messages/platform-team/) channel on the  Mergermarket slack.
* A boilerplate project to start with - try searching the [mergermarket Github organisation](https://github.com/mergermarket/) for repositories with "boilerplate" in the name (check the README too).

## Create initial service

From the root of your workspace (i.e. where you check projects out to) run the following command, substituting in the name of your new service, the boilerplate and team:

    bash <( curl -fsS https://setup.mergermarket.it/setup.sh ) \
        --name <name-of-your-service> \
        --boilerplate <boilerplate-repo> \
        --team <your-team>

_**Note:** if you are uncomfortable with downloading and running this script in a single step, it's also fine to download it and inspect it before running it._

Replace each of the parameter values as described:

* `<name-of-your-service>` - should be lower-case with words separated by hyphens (i.e. "kebab-case"). The Mergermarket convention is to end services that are used by staff with "-admin", to end services used by subscribers with "-subscriber" and to end backend services with "-service".
* `<boilerplate-repo>` - the full git url starting "git@github.com:" or "https://github.com/" -  the protocol chosen here will be used to pull the boilerplate and platform config from Github. As well as configure the remote that will be used for the service repo itself.
* `<your-team>` - the **exact** name of the team as it appears in Jenkins (check the URL in case there is an alias configured) and in the Github team.

If your bolilerplate repository has any templates `*.setup_template` with custom placeholders as `%{NAME}` you can set the values by passing one or more times the option `--setup-var NAME=value`.

If the script completes successfully, you should now have the following:

* A repo in Github including the code from the boilerplate, cloned in your workspace.
* Platform configuration added to your project under `infra/platform-config` (see `infra/platform-config/README.md` for instructions on how to update this in the future).
* A Jenkins pipeline in your team's jenkins folder.

You will most likely need to perform some customisation of the Jenkins pipline specific to your service. The Jenkins pipeline is configured to trigger every time a change is pushed to Github. However, this only happens **after** the first run, so you will have to trigger it manually the first time.

## Customisation

By default the `infra/` folder will contain what's needed for a basic ECS service. This section describes common customisations to this. The mechanism for doing this is in a `service.json` file which should be placed at the root of the project for your service.

At a minimum, the `service.json` will need:

### `TYPE`

For ECS services set this to `docker` (this should be provided by the boilerplate). Additional service types will be made available in the future.

### `TEAM`

This is used to tag the infrastructure for your service, to make it easy to find in monitoring, logging, billing, etc.

### `ACCOUNT_PREFIX`

Mergermarket runs multiple AWS accounts. Accounts are created in pairs, one containing non-production infrastructure with the "dev" postfix (e.g. "mmgdev") and one containing production infrastructure with the "prod" postfix (e.g. "mmgprod"). The other part of the name (i.e. "mmg" in this example) is the _account prefix_. Whatever account you use, there should be a corresponding subfolder inside `infra/platform-config/`.

### `REGION`

This determines the AWS region your service will run in. Before picking a region, you should make sure the platform has infrastructure available there, configured in `infra/platform-config/ACCOUNT_PREFIX/REGION`.

Please see the [service.json reference](/reference/service-json) for more detail.

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
* [Managing secrets](guides/secrets)
* [Adding routes to an existing ALB](guides/adding-routes-to-an-existing-alb)
* [Redirecting HTTP traffic to HTTPS](guides/http-to-https-redirect)

