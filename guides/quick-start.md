---
title: Quick start guide
menu: guides
weight: 1
---

# cdflow quick start

This guide describes how to quickly create a service (clone boilerplate, setup Github repository, setup CI pipeline, etc.) using the Acuris setup service. If you are not working at Acuris you will not have access to the setup service and will need to do these steps manually - see the [Manual Setup guide](./manual-setup).

## Pre-requisites

In order to create a service, you will need:

* You will need to be on the Acuris network. This means either being in the office or using a VPN (search "Platform VPN" in the intranet).
* A team folder in Jenkins and a corresponding team group in Github. If this is a new team, or if you need further guidance ask *@platform* in the [#platform-team](https://mergermarket.slack.com/messages/platform-team/) channel on Mergermarket slack.
* A boilerplate project to start with - try searching the [mergermarket Github organisation](https://github.com/mergermarket/) for repositories with "boilerplate" in the name (check the README too), or ask in #devs or #platform-team on slack to see if we have anything that fits your needs.

## Create initial service

First change directory to the root of your workspace (where you clone repositories), and run the following for a usage message:

    bash <( curl -fsS https://setup.mergermarket.it/setup.sh )

If you don't see a message, or the command just hangs, then this is likely a network issue - see the first prerequisite above.

A full command (including required parameters) will look something like this:

    bash <( curl -fsS https://setup.mergermarket.it/setup.sh ) \
        --name my-amazing-service \
        --boilerplate git@github.com:mergermarket/node-minimal-boilerplate.git \
        --team DevTeam-Banana

### Setup vars

Depending on the boilerplate, you may be prompted to provide additional values for placeholders within the boilerplate. For example, if a boilerplate includes a placeholder `%{fruit}`, then you will be asked to provide the value for that placeholder. This can be done as follows:

    bash <( curl -fsS https://setup.mergermarket.it/setup.sh ) \
        --name my-amazing-service \
        --boilerplate git@github.com:mergermarket/node-minimal-boilerplate.git \
        --team DevTeam-Banana \
        --setup-var fruit=banana

This is just an example and the actual placeholders may not be fruit related at all. In general it is best to refer to the boilerplate documentation to find out what a placeholder is for (e.g. its README).

### Result

If the script completes successfully, you should now have the following:

* A repo in Github including the code from the boilerplate, cloned in your workspace.
* If the boilerplate has a `jenkins-config/` folder contianing a template for the pipeline, you will have a Jenkins pipeline in your team's jenkins folder. The jenkins pipeline is triggered each time a commit is pushed to Github. However you may need to trigger it manually the first time.

## Next steps

* Find out more about the process of setting up a project in the [manual setup guide](manual-setup).
* [Service configuration guide](configuration).
* [Managing secrets](guides/secrets)
* [Adding routes to an existing ALB](guides/adding-routes-to-an-existing-alb)
* [Redirecting HTTP traffic to HTTPS](guides/http-to-https-redirect)

