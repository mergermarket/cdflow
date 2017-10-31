---
menu: reference
weight: 20
---

# Platform Config Folder

This is a directory, passed to the `cdflow release` command with the `--platform-config` flag. It is bundled with the release and contains information about common resources such as VPCs and subnets.

The directory should contain a structure as follows, with a folder for each account alias and JSON files within those which are named after the AWS regions in which you are operating and contain the details of resources within those regions:

```bash
[user@localhost org-platform-config]$ tree
.
├── orgdev
│   └── eu-west-1.json
└── orgprod
    └── eu-west-1.json
```

## File contents

The files are passed to the `terraform` executable as a `-var-file` at deploy time so the file should probably have a top-level key, such as `"platform-config"`. Within the Terraform code this will be available as a map variable and values can be looked up via their key.
