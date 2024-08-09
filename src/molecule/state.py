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
import os

from molecule import util


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


class InvalidState(Exception):  # noqa: N818
    """Exception class raised when an error occurs in :class:`.State`."""


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

    def __init__(self, config) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001
        """Initialize a new state class and returns None.

        Args:
            config: An instance of a Molecule config.
        """
        self._config = config
        self._state_file = self._get_state_file()  # type: ignore[no-untyped-call]
        self._data = self._get_data()  # type: ignore[no-untyped-call]
        self._write_state_file()  # type: ignore[no-untyped-call]

    def marshal(func):  # type: ignore[no-untyped-def]  # noqa: ANN201, N805, D102
        def wrapper(self, *args, **kwargs):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN002, ANN003, ANN202
            func(self, *args, **kwargs)  # type: ignore[operator]  # pylint: disable=not-callable
            self._write_state_file()

        return wrapper

    @property
    def state_file(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._state_file

    @property
    def converged(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._data.get("converged")

    @property
    def created(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._data.get("created")

    @property
    def driver(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._data.get("driver")

    @property
    def prepared(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._data.get("prepared")

    @property
    def run_uuid(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._data.get("run_uuid")

    @property
    def is_parallel(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._data.get("is_parallel")

    @property
    def molecule_yml_date_modified(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._data.get("molecule_yml_date_modified")

    @marshal  # type: ignore[arg-type]
    def reset(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        self._data = self._default_data()  # type: ignore[no-untyped-call]

    @marshal  # type: ignore[arg-type]
    def change_state(self, key, value):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
        """Change the state of the instance data with the given `key` and the provided ``value`.

        Wrapping with a decorator is probably not necessary.

        Args:
            key: A ``str`` containing the key to update
            value: A value to change the ``key`` to
        """
        if key not in VALID_KEYS:
            raise InvalidState
        self._data[key] = value

    def _get_data(self):  # type: ignore[no-untyped-def]  # noqa: ANN202
        if os.path.isfile(self.state_file):  # noqa: PTH113
            return self._load_file()  # type: ignore[no-untyped-call]
        return self._default_data()  # type: ignore[no-untyped-call]

    def _default_data(self):  # type: ignore[no-untyped-def]  # noqa: ANN202
        return {
            "converged": False,
            "created": False,
            "driver": None,
            "prepared": None,
            "molecule_yml_date_modified": None,
            "run_uuid": self._config._run_uuid,  # noqa: SLF001
            "is_parallel": self._config.is_parallel,
        }

    def _load_file(self):  # type: ignore[no-untyped-def]  # noqa: ANN202
        return util.safe_load_file(self.state_file)

    def _write_state_file(self):  # type: ignore[no-untyped-def]  # noqa: ANN202
        util.write_file(self.state_file, util.safe_dump(self._data))

    def _get_state_file(self):  # type: ignore[no-untyped-def]  # noqa: ANN202
        return os.path.join(self._config.scenario.ephemeral_directory, "state.yml")  # noqa: PTH118
