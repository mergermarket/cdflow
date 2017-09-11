# CDFlow

## Introduction to cdflow

This documentation should give you everything you need to get a service, lambda function, or infrastructure definition up and running using cdflow. We aim to cover what cdflow is, what the use case is, and what problems it can help solve. Finally, how you can help make cdflow better.

If you are ready to jump in and get started setting up a service, we'd suggest going to the [getting started guide](guides/getting-started).

If you already know the basics, head over to the [full documentation]() section.

What is cdflow?
---------------

Cdflow helps you continuously deliver your software. It can build, deploy and destroy your applications through code; allowing you to manage versions of your infrastructure through source control. It uses [Terraform](https://www.terraform.io/intro/index.html) for it's "Infrastructure as Code" foundations but lowers the barrier to entry by enforcing conventions on the project structure.

You can find out more about those conventions in the [full documentation]().

Supported Use Cases
--------------------

These are some concrete use cases where cdflow is well suited and proven, however this list is not extensive and we encourage you to explore use cases not covered here.





Contributing
------------

All contributions are welcome. We encourage you raise issues and pull requests to help us make cdflow better. Although we don't have the capacity to validate and fix every issue that may come in. We do endeavour to respond to all issues, and merge PRs in due time.

For pull requests, we require a tests to replicate your issue or feature and to follow our style guide. We use PEP 8 style for Python and have a linter that should display any issues. You can run the tests with the `tests.sh` script in the root of both the [cdflow]() and [cdflow-docker-image]() when making changes.
