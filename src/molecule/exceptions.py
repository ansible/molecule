"""Custom Molecule exceptions."""

from __future__ import annotations

import logging

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Sequence
    from warnings import WarningMessage


LOG = logging.getLogger(__name__)


class MoleculeError(Exception):
    """Generic Molecule error."""

    def __init__(
        self,
        message: str = "",
        code: int = 1,
        warns: Sequence[WarningMessage] = (),
    ) -> None:
        """Custom exception to handle scenario run failures.

        Args:
            message: The message to display about the problem.
            code: Exit code to use when exiting.
            warns: Warnings about the problem to issue.
        """
        super().__init__()

        if message:
            LOG.critical(message, extra={"highlighter": False})

        for warn in warns:
            LOG.warning(warn.__dict__["message"].args[0])

        self.code = code


class ScenarioFailureError(MoleculeError):
    """Details about a scenario that failed."""
