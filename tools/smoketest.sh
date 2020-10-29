#!/bin/bash

ANSIBLE=$(pipdeptree --reverse -p ansible)

if [ -z "$ANSIBLE" ]; then
    echo "Ansible dependency not detected."
else
    echo "FATAL: Detected unexpected dependency on Ansible package"
    echo "$ANSIBLE"
    exit 2
fi
