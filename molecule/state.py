#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

import os

from molecule import logger
from molecule import util

LOG = logger.get_logger(__name__)
VALID_KEYS = [
    'created',
    'converged',
    'driver',
    'prepared',
]


class InvalidState(Exception):
    """
    Exception class raised when an error occurs in :class:`.State`.
    """
    pass


class State(object):
    """
    A class which manages the state file.  Intended to be used as a singleton
    throughout a given Molecule config.  The initial state is serialized to
    disk if the file does not exist, otherwise is deserialized from the
    existing state file.  Changes made to the object are immediately
    serialized.

    State is not a top level option in Molecule's config.  It's purpose is for
    bookkeeping, and each Config_ object has a reference to a State_ object.

    .. note::

        Currently, it's use is significantly smaller than it was in v1 of
        Molecule.
    """

    def __init__(self, config):
        """
        Initialize a new state class and returns None.

        :param config: An instance of a Molecule config.
        :returns: None
        """
        self._config = config
        self._state_file = self._get_state_file()
        self._data = self._get_data()
        self._write_state_file()

    def marshal(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._write_state_file()

        return wrapper

    @property
    def state_file(self):
        return self._state_file

    @property
    def converged(self):
        return self._data.get('converged')

    @property
    def created(self):
        return self._data.get('created')

    @property
    def driver(self):
        return self._data.get('driver')

    @property
    def prepared(self):
        return self._data.get('prepared')

    @marshal
    def reset(self):
        self._data = self._default_data()

    @marshal
    def change_state(self, key, value):
        """
        Changes the state of the instance data with the given
        ``key`` and the provided ``value``.

        Wrapping with a decorator is probably not necessary.

        :param key: A ``str`` containing the key to update
        :param value: A value to change the ``key`` to
        :return: None
        """
        if key not in VALID_KEYS:
            raise InvalidState
        self._data[key] = value

    def _get_data(self):
        if os.path.isfile(self.state_file):
            return self._load_file()
        return self._default_data()

    def _default_data(self):
        return {
            'converged': False,
            'created': False,
            'driver': None,
            'prepared': None,
        }

    def _load_file(self):
        return util.safe_load_file(self.state_file)

    def _write_state_file(self):
        util.write_file(self.state_file, util.safe_dump(self._data))

    def _get_state_file(self):
        return os.path.join(self._config.scenario.ephemeral_directory,
                            'state.yml')
