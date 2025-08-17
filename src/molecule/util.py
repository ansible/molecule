"""Compatibility module for util imports.

This module provides backward compatibility for third-party plugins
that import from the old location. New code should import from
molecule.utils.util instead.
"""

from __future__ import annotations

import warnings

# Import everything from the new location
from molecule.utils.util import *  # noqa: F403


# Issue a deprecation warning when this module is imported
warnings.warn(
    "Importing from 'molecule.util' is deprecated. Use 'from molecule.utils import util' instead.",
    DeprecationWarning,
    stacklevel=2,
)
