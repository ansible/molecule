#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
"""State Module."""
from __future__ import annotations

import logging

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict, TypeVar, cast

from molecule import util


if TYPE_CHECKING:

    from molecule.config import Config


LOG = logging.getLogger(__name__)
VALID_KEYS = [
    "created",
    "converged",
    "driver",
    "prepared",
    "run_uuid",
    "is_parallel",
    "molecule_yml_date_modified",
]
F = TypeVar("F", bound=Callable[..., None])


class InvalidState(Exception):  # noqa: N818
    """Exception class raised when an error occurs in :class:`.State`."""


class StateData(TypedDict):
    """Valid state values and types.

    Attributes:
        converged: Has scenario converged.
        created: Has scenario been created:
        driver: Driver for scenario.
        prepared: Has scenario prepare run.
        molecule_yml_date_modified: Modified date of molecule.yml file.
        run_uuid: UUID of active run.
        is_parallel: Is this run parallel.
    """

    converged: bool
    created: bool
    driver: str | None
    prepared: bool
    molecule_yml_date_modified: float | None
    run_uuid: str
    is_parallel: bool


def marshal(func: F) -> F:
    """Decorator to immediately write state to file after call finishes.

    Args:
        func: Function to decorate.

    Returns:
        Decorated function.
    """

    def wrapper(self: State, *args: object, **kwargs: object) -> None:
        func(self, *args, **kwargs)
        self._write_state_file()

    return cast(F, wrapper)


class State:
    """A class which manages the state file.

    Intended to be used as a singleton throughout a given Molecule config.
    The initial state is serialized to disk if the file does not exist,
    otherwise is deserialized from the existing state file.  Changes made to
    the object are immediately serialized.

    State is not a top level option in Molecule's config.  It's purpose is for
    bookkeeping, and each :class:`.Config` object has a reference to a State_
    object.

    !!! note

        Currently, it's use is significantly smaller than it was in v1 of
        Molecule.
    """

    def __init__(self, config: Config) -> None:
        """Initialize a new state class and returns None.

        Args:
            config: An instance of a Molecule config.
        """
        self._config = config
        self._state_file = self._get_state_file()
        self._data = self._get_data()
        self._write_state_file()

    @property
    def state_file(self) -> str:
        """State file path.

        Returns:
            Path to the state file.
        """
        return str(self._state_file)

    @property
    def converged(self) -> bool:
        """Is run converged.

        Returns:
            Whether the run has converged.
        """
        return self._data["converged"]

    @property
    def created(self) -> bool:
        """Has scenario been created.

        Returns:
            Whether scenario has been created.
        """
        return self._data["created"]

    @property
    def driver(self) -> str | None:
        """Driver for scenario.

        Returns:
            Name of the driver for the scenario.
        """
        return self._data["driver"]

    @property
    def prepared(self) -> bool:
        """Has scenario prepare run.

        Returns:
            Whether scenario prepare has run.
        """
        return self._data["prepared"]

    @property
    def run_uuid(self) -> str:
        """Scenario run UUID.

        Returns:
            The UUID for this scenario run.
        """
        return self._data["run_uuid"]

    @property
    def is_parallel(self) -> bool:
        """Is molecule in parallel mode.

        Returns:
            Whether Molecule is in parallel mode.
        """
        return self._data["is_parallel"]

    @property
    def molecule_yml_date_modified(self) -> float | None:
        """The modified date of molecule.yml.

        Returns:
            The timestamp of the last modification date of molecule.yml.
        """
        return self._data["molecule_yml_date_modified"]

    @marshal
    def reset(self) -> None:
        """Reset state data."""
        self._data = self._default_data()

    @marshal
    def change_state(self, key: str, value: object) -> None:
        """Change the state of the instance data with the given `key` and the provided ``value`.

        Wrapping with a decorator is probably not necessary.

        Args:
            key: A ``str`` containing the key to update
            value: A value to change the ``key`` to

        Raises:
            InvalidState: if an invalid key is requested.
        """
        if key not in VALID_KEYS:
            raise InvalidState
        self._data[key] = value  # type: ignore[literal-required]

    def _get_data(self) -> StateData:
        if self._state_file.is_file():
            return self._load_file()
        return self._default_data()

    def _default_data(self) -> StateData:
        return {
            "converged": False,
            "created": False,
            "driver": None,
            "prepared": False,
            "molecule_yml_date_modified": None,
            "run_uuid": self._config._run_uuid,  # noqa: SLF001
            "is_parallel": self._config.is_parallel,
        }

    def _load_file(self) -> StateData:
        return cast(StateData, util.safe_load_file(self._state_file))

    def _write_state_file(self) -> None:
        util.write_file(self.state_file, util.safe_dump(self._data))

    def _get_state_file(self) -> Path:
        return Path(self._config.scenario.ephemeral_directory) / "state.yml"
