"""Custom Molecule exceptions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Mapping
    from warnings import WarningMessage


class ScenarioFailureError(Exception):
    """Details about a scenario that failed."""

    def __init__(
        self,
        message: str = "",
        code: int = 1,
        detail: Mapping[str, Any] | None = None,
        warns: tuple[WarningMessage, ...] = (),
    ) -> None:
        """Custom exception to handle scenario run failures.

        Args:
            message: The message to display about the problem.
            code: Exit code to use when exiting.
            detail: Complex information related to the problem.
            warns: Warnings about the problem to issue.
        """
        super().__init__()

        self.message = message
        self.code = code
        self.detail = detail
        self.warns = warns
