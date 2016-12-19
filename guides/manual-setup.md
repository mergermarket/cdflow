# Mergermarket infra scripts - manual setup

This guide walks you through setting up a new service based on the [Mergermarket infra scripts](https://mergermarket.github.io/infra/). The guide is slightly longer winded than the [Quick-start guide](./quick-start) and is intended for the first time you set up a service in order to fully understand all the steps.

## 1. Create a github repository for your service

Create a repository in Github and clone it on your computer. If you are developing a service for Mergermarket, do this at [github.com/organizations/mergermarket/repositories/new](https://github.com/organizations/mergermarket/repositories/new).

## 2. Including _infra_ in your repository

This pulls Mergermarket infra scripts into the `infra/` folder into your repository. This mechanism means you do not have external dependencies when you come to release or deploy your service, and puts you in control of when you take updates. This folder contains:

* Scripts for releasing and deploying your code.
* A [Terraform](https://www.terraform.io/) module that will be used to create the infrastructure for your service in each environment.
* Boilerplate Terraform code for your service that will use the above module. You will customise this for your service.

From the root of your freshly cloned service, run:

    git pull --allow-unrelated-histories --no-edit \
      git@github.com:mergermarket/infra.git master
    
If you prefer to clone via HTTPS, use this command instead:
    
    git pull --allow-unrelated-histories --no-edit \
      https://github.com/mergermarket/infra.git master

The above commands pull the Git history of the _infra_ project into your repository. This allows future updates to be pulled into your repository and be merged with any customisations you have made with the `infra/` folder - i.e. it is by design (the `--squash` option shiould be avoided).

### Push changes

Complete this step by pushing changes to Github:

    git push

### Pulling in future updates

To pull in future updates, simply run:

    git pull --no-edit \
      git@github.com:mergermarket/infra.git master

Or, if you prefer to clone over HTTPS:

    git pull --no-edit \
      https://github.com/mergermarket/infra.git master


## 3. Include platform config info your repository

The above are generic scripts for releasing, creating/updating infrastructure, and deploying your service onto that infrastructure, designed not to be specific to Mergermarket. However, this depends on certain AWS infrastructure already existing (e.g. AWS accounts, VPCs, ECS clusters, etc). This depends on the organisation that you are deploying your service. Within Mergermarket this is provided by pulling the [mmg-platform-config](https://github.com/mergermarket/mmg-platform-config) repository into your repository:

    git pull --allow-unrelated-histories --no-edit \
    	 git@github.com:mergermarket/mmg-platform-config.git master

Or, if you prefer to clone over HTTPS:

    git pull --allow-unrelated-histories --no-edit \
        https://github.com/mergermarket/mmg-platform-config.git master

This brings in files containing the values for [Terraform input variables](https://www.terraform.io/intro/getting-started/variables.html#from-a-file) included via a `-var-file=infra/platform-config/ACCOUNT_PREFIX/prod/REGION.json` option, where `ACCOUNT_PREFIX` and `REGION` depend on metadata you set in your service (see step 4 below).

This will pull in the `infra/platform-config/` folder containing As above, this is designed to allow changes to be pulled in easily.

### Push changes

Complete this step by pushing changes to Github:

    git push

### Pulling in future platform config updates

To pull in future updates:

    git pull --no-edit \
      git@github.com:mergermarket/mmg-platform-config.git master

Or, if you prefer to clone over HTTPS:

    git pull --no-edit \
      https://github.com/mergermarket/mmg-platform-config.git master

## 4. Add metadata to your service

The scripts require a metadata file called `service.json` in the root of your project:

    {
      "TEAM": "your-team-name",
      "ACCOUNT_PREFIX": "mmg",
      "REGION": "eu-west-1"
    }

* `TEAM` is the only required key, and names the team that is responsible for running this service.
* `ACCOUNT_PREFIX` (as well as `REGION`) determines which files to select in the `infra/platform-config/` folder - it default sto `"mmg"`. The scripts separate infrastructure between production and non-production environments into separate AWS accounts. These accounts are named with the supplied prefix, combined with either the `"dev"` or `"prod"` postfix - e.g. if you `ACCOUNT_PREFIX` is `"mmg"`, then your service will be deployed in the `"mmgdev"` and `"mmgprod"` accounts, selecting platform config from the `infra/platform-config/mmg/dev/` and `infra/platform-config/mmg/prod/` folders.
* `REGION` (default `"eu-west-1"`) specifies the region the service should be deployed in - the infra scripts currently support deploying each service into a single region. The region (with a `.json` extension) is the filename of the file under `infra/platfrom-config` (e.g. `infra/platform-config/mmg/dev/eu-west-1.json`).

### Commit and push changes

Complete this step by committing your change and pushing it to Github:

    git add service.json
    git commit -m 'Service metadata'
    git push

## 5. Add code for your service

This step is highly dependent on the service you are developing. This will set up a simple HTTP service based on the [official node docker image](https://hub.docker.com/_/node/) listing on port `8000` (the default expected by the infrastructure definition).

### `package.json`

To create a basic `package.json` in your project, run `npm init` accepting the defaults.

### `server.js`

Create `server.js` in the root of the repository containing the following:

    require('http').createServer((req, res) => {
      res.writeHead(200, { 'Content-Type' : 'text/plain' })
      res.end('Hello, World!')
    }).listen(8000)

### `Dockerfile`

Create `Dockerfile` in the root of the repository containing the following:

	FROM node:7-alpine
	
	RUN mkdir -p /usr/src/app
	WORKDIR /usr/src/app
	
	COPY package.json /usr/src/app/
	RUN npm install
	ONBUILD COPY . /usr/src/app
	
	CMD [ "npm", "start" ]

### Commit and push changes

Complete this step by committing your changes and pushing them to Github:

    git add package.json server.js Dockerfile
    git commit -m 'Basic service'
    git push

## 6. Review your infrastructure

The Terraform code that defines your infrastructure is at the top level in the `infra/` folder. By convention the main entry-point it the `infra/main.tf` file. Most of this is boilerplate that provides sensible defaults for your infrastructure, but one thing you may need to change is the value of the `dns-domain` parameter to the `ecs-service` module (near the bottom of the file).

By default the `ecs-service` module will create an [Application Load Balancer](https://aws.amazon.com/elasticloadbalancing/applicationloadbalancer/) for your service in each environment, along with a DNS name in Route53 for your service. The valuye of `dns-domain` must correspond to a domain that is configured in the platform config that you've pulled in, so that the DNS name can be created in the appropriate Route53 hosted zone, and so that an SSL certificate can be associated with the load balancer.

## 7. Release your service

To test the process of creating a release, run:

    infra/scripts/release

If everything works as intended, you should see the output from a docker build ending lines similar to:

    infra/scripts/release: image IMAGE_URL:dev successfully built
    infra/scripts/release: no version supplied, push skipped
    infra/scripts/release: done.

The remaining steps should normally be initiated from a shared build server (e.g. Jenkins), after the code is pushed to Github. However, this guide will walk through running them locally to demonstrate how they work. Before you continue you will need to have AWS credentials configured that are permitted to assume the `admin` role within the accounts you will be deploying into (e.g. `mmgdev` and `mmgprod`).

In order to build a version other than `"dev"` and to push it to the [EC2 Container Registry (ECR)](https://aws.amazon.com/ecr/), you must specify a version number:

    infra/scripts/release 1

If everything worked as intended, this should result in your new docker image being pushed.

## 8. Deploy your service

To deploy your service, run the command:

    infra/scripts/deploy aslive 1

This will run `terraform plan` followed by `terraform apply` via [Terragrunt](https://github.com/gruntwork-io/terragrunt). In the output look out for lines like:

    [terragrunt] 2017/01/01 00:00:00 Running command: terraform plan \
      -var component=your-component -var aws_region=eu-west-1 -var env=aslive \
      -var image=IMAGE_URL:1 -var team=your-team -var version="1" \
      -var-file infra/platform-config/mmg/dev/eu-west-1.json infra

..and:

    [terragrunt] 2017/01/01 00:00:00 Running command: terraform apply \
      -var component=your-component -var aws_region=eu-west-1 -var env=aslive \
      -var image=IMAGE_URL:1 -var team=your-team -var version="1" \
      -var-file infra/platform-config/mmg/dev/eu-west-1.json infra

Most of the remaining output is that of Terraform as it creates the infrastructure for your service in the `aslive` environment, including a service running your code in the [EC2 Container Service (ECS)](https://aws.amazon.com/ecs/) service. The output should also include the `name` attribute within the `module.ecs-service.aws_route53_record.dns_record` section, which is the name of your service according to the `domain-name` you chose above, as well as the naming conventions - the resulting URL will be something like:

    https://aslive-your-service-name.dev.mmgapi.net





