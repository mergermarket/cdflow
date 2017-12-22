---
title: Setting Secrets
menu: guides
weight: 50
---

# Setting Secrets

Cdflow uses [Credstash](https://github.com/fugue/credstash) to inject secrets into your infrastructure. Credstash is a utility that encrypts/decrypts secrets using a KMS key. The tool also uses a DynamoDb table in order to persist secrets.

When adding secrets to credstash, cdflow will look for any keys in DynamoDB that uses the following format:

```
deploy.<environment_name>.<service_name>.<key_name>
```

As an example:

```
deploy.live.database-sevice.DB_CONNECT_STRING = 'some-super-secret-password!'
```

Cdflow then adds them to a `secrets` variable that can be passed to your Terraform configuration files.

```
variable "secrets" {
  type        = "map"
  description = "Secret credentials fetched using credstash"
  default     = {}
}
```

The map itself will be in the format `{ <key_name> : <value> }`. So using the example above the `secrets` map would be:

```
{
  DB_CONNECT_STRING = 'some-super-secret-password!'
}
```
