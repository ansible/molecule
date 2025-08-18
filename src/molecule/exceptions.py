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
    ) -> None:
        """Generic exception for molecule errors.

        Args:
            message: The message to display about the problem.
            code: Exit code to use when exiting.
        """
        super().__init__()
        self.code = code
        self.message = message

        if message:
            LOG.critical(message, extra={"highlighter": False})


class ScenarioFailureError(MoleculeError):
    """Details about a scenario that failed."""

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
        super().__init__(message, code)

        for warn in warns:
            LOG.warning(warn.message)


class ImmediateExit(Exception):  # noqa: N818
    """Exception for immediate program termination.

    Provides SystemExit-like behavior (immediate program termination with exit codes)
    but implemented as an Exception subclass for better integration with exception
    handling frameworks and existing Molecule patterns.

    Unlike SystemExit which inherits from BaseException, this inherits from Exception
    to ensure it can be caught by standard exception handlers while still providing
    the immediate exit semantics we need.
    """

    def __init__(self, message: str, code: int) -> None:
        """Initialize immediate exit exception.

        Args:
            message: Message to display about the exit reason.
            code: Exit code (0 for success, non-zero for failure).
        """
        super().__init__(message)
        self.message = message
        self.code = code
