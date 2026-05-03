"""Tests for molecule.app module."""
# pylint: disable=redefined-outer-name

from __future__ import annotations

import subprocess

from typing import TYPE_CHECKING, cast
from unittest.mock import MagicMock, patch

import pytest

from molecule.app import App


if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def app_instance(tmp_path: Path) -> App:
    """Create an App instance with a mocked runtime.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        App instance with mocked runtime.
    """
    with patch("molecule.app.Runtime") as mock_runtime_cls:
        mock_runtime = MagicMock()
        mock_runtime.environ = {
            "ANSIBLE_ROLES_PATH": "/project/roles:/usr/share/ansible/roles",
            "ANSIBLE_LIBRARY": "/project/plugins/modules",
            "HOME": "/home/testuser",
        }
        mock_runtime.run.return_value = subprocess.CompletedProcess(
            args=["echo", "test"],
            returncode=0,
            stdout="",
            stderr="",
        )
        mock_runtime_cls.return_value = mock_runtime
        return App(tmp_path)


class TestAppRunCommand:
    """Tests for App.run_command environment handling."""

    def test_run_command_uses_runtime_environ_when_env_is_none(
        self,
        app_instance: App,
    ) -> None:
        """Verify that run_command passes runtime.environ when no env is given.

        Args:
            app_instance: Molecule app instance.
        """
        app_instance.run_command(["echo", "hello"])

        # Use cast to avoid mypy error: "Runtime" has no attribute "run" that is a Mock
        mock_run = cast("MagicMock", app_instance.runtime.run)
        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs["env"] is app_instance.runtime.environ

    def test_run_command_merges_runtime_environ_with_custom_env(
        self,
        app_instance: App,
    ) -> None:
        """Verify that run_command merges runtime.environ with a custom env dict.

        This is the critical fix: previously, passing a custom env would
        completely replace runtime.environ, losing ANSIBLE_ROLES_PATH and
        other auto-discovered paths.

        Args:
            app_instance: Molecule app instance.
        """
        custom_env = {
            "MY_CUSTOM_VAR": "custom_value",
            "ANSIBLE_CONFIG": "/project/ansible.cfg",
        }

        app_instance.run_command(["echo", "hello"], env=custom_env)

        mock_run = cast("MagicMock", app_instance.runtime.run)
        call_kwargs = mock_run.call_args
        merged_env = call_kwargs.kwargs["env"]

        # Runtime environ keys must survive the merge
        assert "ANSIBLE_ROLES_PATH" in merged_env
        assert merged_env["ANSIBLE_ROLES_PATH"] == "/project/roles:/usr/share/ansible/roles"

        # Custom env keys must also be present
        assert merged_env["MY_CUSTOM_VAR"] == "custom_value"
        assert merged_env["ANSIBLE_CONFIG"] == "/project/ansible.cfg"

    def test_run_command_custom_env_overrides_runtime_environ(
        self,
        app_instance: App,
    ) -> None:
        """Verify that custom env values take precedence over runtime.environ.

        Args:
            app_instance: Molecule app instance.
        """
        custom_env = {
            "HOME": "/override/home",
        }

        app_instance.run_command(["echo", "hello"], env=custom_env)

        mock_run = cast("MagicMock", app_instance.runtime.run)
        call_kwargs = mock_run.call_args
        merged_env = call_kwargs.kwargs["env"]

        # Custom value should override the runtime value
        assert merged_env["HOME"] == "/override/home"

        # But runtime-only keys must still be present
        assert "ANSIBLE_ROLES_PATH" in merged_env

    def test_run_command_preserves_ansible_paths_in_merged_env(
        self,
        app_instance: App,
    ) -> None:
        """Verify ANSIBLE_ROLES_PATH and ANSIBLE_LIBRARY survive env merging.

        This directly tests the bug scenario: Molecule's provisioner passes
        a custom env dict, which previously wiped out the paths that
        ansible-compat had carefully set up.

        Args:
            app_instance: Molecule app instance.
        """
        provisioner_env = {
            "ANSIBLE_CONFIG": "/project/ansible.cfg",
            "ANSIBLE_FORCE_COLOR": "true",
        }

        app_instance.run_command(["ansible-playbook", "converge.yml"], env=provisioner_env)

        mock_run = cast("MagicMock", app_instance.runtime.run)
        call_kwargs = mock_run.call_args
        merged_env = call_kwargs.kwargs["env"]

        # These paths are critical and must never be lost
        assert "ANSIBLE_ROLES_PATH" in merged_env, (
            "ANSIBLE_ROLES_PATH was lost during env merge — this causes role discovery failures"
        )
        assert "ANSIBLE_LIBRARY" in merged_env, (
            "ANSIBLE_LIBRARY was lost during env merge — this causes module discovery failures"
        )
