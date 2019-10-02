#!/bin/bash

set -euo pipefail

sed -i -e "s/version='dev'/version='$(git describe --tag)'/" setup.py

python setup.py sdist

twine upload ./dist/*
