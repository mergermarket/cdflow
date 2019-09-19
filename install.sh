#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

command_url="https://raw.githubusercontent.com/mergermarket/cdflow/master/cdflow.py"
man_url="https://raw.githubusercontent.com/mergermarket/cdflow/master/docs/cdflow.1"
command_path="/usr/local/bin/cdflow"
man_path="/usr/local/share/man/man1/cdflow.1"

# install cdflow command
curl $command_url > $command_path
chmod 744 $command_path

# install python3 dependencies
pip3 install -U docker boto3 PyYAML dockerpty

# install manpage
curl $man_url > $man_path

# verify
if  which -s cdflow ; then
  printf "\n\tcdflow installed successfully\n\n"
else
  printf "\n\tcdflow was not installed successfully\n\n"
fi