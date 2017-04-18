---
title: Redirecting HTTP traffic to HTTPS
menu: guides
weight: 6
---

## Summary

By default services listen only for HTTPS requests (on port 443). This can be
confusing for users if they visit the HTTP equivalent URL since the connection
will be refused. This guide describes how to ensure users are properly
redirected.

## Prerequisites

Your service must have its own Application Load Balancer - i.e. no
`alb_listener_arn` parameter is passed to the `ecs-service` Terraform module
in `infra/main.tf`.

## Configuration

Add the following parameter to the `ecs-service` Terraform module in
`infra/main.tf`:

```
  force_https           = "true" 
```

## Details

This will cause an additional ECS service running the
[https-redirector](https://hub.docker.com/r/mergermarket/https-redirector/)
image to do the redirection. This will receive HTTP requests from your load
balancer.

