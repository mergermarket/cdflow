# Outline for cdflow docs

```
Introduction
|_ Setup a service
| |_ Setup a frontend service?
| |_ Setup a backend service?
| |_ Setup a Lambda function
| |_ Setup infrastucture
|_ Full Documentation
| |_ cdflow
| |_|_ Installation
| |_|_ Usage
| |_|_ Development notes
| |_ cdflow-docker-image
| |_|_ Installation
| |_|_ Usage
| |_|_ Managing Secrets
| |_|_ Terraform
| |_|_|_ Links and description to relevant terraform modlues we use
|_ Contribution Guidelines
```

## Tools

- ~**cdflow**~ (Public, README.md & [cdflow docs](https://mergermarket.github.io/cdflow))
	- Installation on Jenkins
	- Usage
	- Development notes
		- How to run tests
- ~**cdflow-docker-image**~ (Public, README.md)
	- Usage (Refer to [cdflow docs](https://mergermarket.github.io/cdflow))
	- Development notes
		- How to run tests
		- Terraform files
		- Terraform modules
	__Description and link to each module in cdflow-docker-image README.md__
			- tf_ecs_service_infrastructure (Public)
			- tf_route53_dns (Public)
			- tf_alb_listener_rules (Public)
			- tf_ecs_update_monitor (Public)
			- tf_load_balanced_ecs_service (Public)
			- tf_ecs_task_definition (Public)
			- tf_ecs_container_definition (Public)

## Using cdflow to setup a service
- Quick start guide
- Full walkthrough
	- Suggested project structure including terraform files & modules

## Using cdflow to setup infrastructure
- Quick start guide
- Full walkthrough
	- Suggested project structure including terraform files & modules

## Using cdflow to setup a lambda function
- Quick start guide
- Full walkthrough
	- Suggested project structure including terraform files & modules

