"""Constants used by molecule."""

from __future__ import annotations

import os


# Exit codes
RC_SUCCESS = 0
RC_TIMEOUT = 3
RC_SETUP_ERROR = 4  # Broken setup, like missing Ansible
RC_UNKNOWN_ERROR = 5  # Unexpected errors for which we do not have more specific codes, yet

# File and directory patterns
MOLECULE_HEADER = "# Molecule managed"
MOLECULE_GLOB = os.environ.get("MOLECULE_GLOB", "molecule/*/molecule.yml")

# Default values
MOLECULE_DEFAULT_SCENARIO_NAME = "default"
MOLECULE_PLATFORM_NAME = os.environ.get("MOLECULE_PLATFORM_NAME", None)
