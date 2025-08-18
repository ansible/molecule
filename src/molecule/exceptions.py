"""Custom Molecule exceptions."""

from __future__ import annotations

import logging


LOG = logging.getLogger(__name__)


class MoleculeError(Exception):
    """Generic Molecule error."""

    def __init__(
        self,
        message: str = "",
        code: int = 1,
    ) -> None:
        """Custom exception to handle scenario run failures.

        Args:
            message: The message to display about the problem.
            code: Exit code to use when exiting.
        """
        super().__init__()
        self.code = code
        self.message = message


class ScenarioFailureError(MoleculeError):
    """Details about a scenario that failed."""


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
