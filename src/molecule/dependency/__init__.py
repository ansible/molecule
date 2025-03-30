"""Dependency module."""

from __future__ import annotations

from .ansible_dependency import AnsibleDependency
from .shell import ShellDependency


__all__ = ["AnsibleDependency", "ShellDependency"]
