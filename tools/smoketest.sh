#!/bin/bash

ANSIBLE=$(uv pip tree --invert --package ansible-core --strict)

if [ -z "$ANSIBLE" ]; then
    echo "Ansible dependency not detected."
else
    echo "FATAL: Detected unexpected dependency on Ansible package"
    echo "$ANSIBLE"
    exit 2
fi
