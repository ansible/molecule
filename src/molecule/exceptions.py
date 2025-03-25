"""Custom Molecule exceptions."""

from __future__ import annotations

import logging

from typing import TYPE_CHECKING, Any

from molecule.util import safe_dump


if TYPE_CHECKING:
    from collections.abc import Mapping
    from warnings import WarningMessage


LOG = logging.getLogger(__name__)


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

        # detail is usually a multi-line string which is not suitable for normal
        # logger.
        if detail:
            detail_str = safe_dump(detail) if isinstance(detail, dict) else str(detail)
            print(detail_str)  # noqa: T201

        if message:
            LOG.critical(message, extra={"highlighter": False})

        for warn in warns:
            LOG.warning(warn.__dict__["message"].args[0])

        self.code = code
