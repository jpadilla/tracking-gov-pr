#!/bin/bash

poetry run tracking-gov-pr root-domains > .amass/domains.txt

docker run -v "$(pwd)/.amass":/.config/amass/ caffix/amass \
  enum -v -src -ip -brute -min-for-recursive 2 -df /.config/amass/domains.txt

cp .amass/amass.json data/amass-enum.jsonl
