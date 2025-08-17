#!/usr/bin/env python3
"""Test script to verify env file support works."""

from __future__ import annotations

import tempfile

from pathlib import Path


# Test env file creation
with tempfile.TemporaryDirectory() as temp_dir:
    env_file = Path(temp_dir) / ".env.yml"
    env_file.write_text("""
MOLECULE_REPORT: true
MOLECULE_COMMAND_BORDERS: false
""")

    print(f"Created env file: {env_file}")
    print(f"Contents:\n{env_file.read_text()}")

    # Test that our env file loading would work
    from molecule.config import set_env_from_file

    test_env = {"EXISTING": "value"}
    merged_env = set_env_from_file(test_env, str(env_file))

    print(f"Merged environment: {dict(merged_env)}")
    print(f"MOLECULE_REPORT from env file: {merged_env.get('MOLECULE_REPORT')}")
    print(f"MOLECULE_COMMAND_BORDERS from env file: {merged_env.get('MOLECULE_COMMAND_BORDERS')}")
