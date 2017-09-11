---
title: Using AWS resources
menu: guides
weight: 99
---

# Using AWS resources

This document describes how to provision and access AWS resource from your
cdflow managed service.

## Creating resources

To create a resource, simply add to your `infra/main.tf`. For example, to
create an SQS queue:

    resource "aws_sqs_queue" "queue" {
      name = "${var.env}-${var.component}-event-queue"
    }

## Granting access to resources

The `ecs-service` terraform module has support for creating an
[IAM Role](http://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)
for your service, which can allow it to access AWS resources without needing to
manage credentials (credentials are retrieved automatically when you use an AWS
SDK or command-line tool. This IAM role is created when you set pass the
`task_policy` parameter to the module, supplying a valid
[IAM policy document](http://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html).

For example, to add a policy that allows your service to send messages to the
queue, your `infra/main.tf` would look like:

    resource "aws_sqs_queue" "queue" {
      name = "${var.env}-${var.component}-event-queue"
    }
    
    module "ecs-service" {
      source = "./modules/ecs-service"
      
      task_policy = <<END
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue.queue.arn}"
        }
      ]
    }
    END
      
      # ...
    }

## Accessing the resource

The final part of the puzzle is how we provide the service with configuration
about the resource in order to access it. This may be the
[ARN](http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html),
or may be some other attribute of the queue. In the case of our SQS queue we
need the queue url, which is accessed via the
[`id` attribute](https://www.terraform.io/docs/providers/aws/r/sqs_queue.html#id).
The `ecs-service` module includes the `infra_container_env` parameter to allow
additional environment variables to be provided for infrastructure
configuration like this:

    resource "aws_sqs_queue" "queue" {
      name = "${var.env}-${var.component}-event-queue"
    }
    
    module "ecs-service" {
      source = "./modules/ecs-service"
      
      task_policy = <<END
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue.queue.arn}"
        }
      ]
    }
    END
      
      infra_container_env = {
        QUEUE_URL = "${aws_sqs_queue.queue.id}"
      }
      
      # ...
    }



