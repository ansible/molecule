"""Constants used by molecule."""

from __future__ import annotations


RC_SUCCESS = 0
RC_TIMEOUT = 3
RC_SETUP_ERROR = 4  # Broken setup, like missing Ansible
RC_UNKNOWN_ERROR = 5  # Unexpected errors for which we do not have more specific codes, yet


MOLECULE_HEADER = "# Molecule managed"
