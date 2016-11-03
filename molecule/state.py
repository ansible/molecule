#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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
"""
A class which manages the state file.  Intended to be used as a singleton
throughout molecule.  The initial state is serialized to disk if the file does
not exist, otherwise is deserialized from the existing state file.  Changes
made to the object are immediately serialized.
"""

import os

import yaml

from molecule import util

VALID_KEYS = [
    'converged',
    'created',
    'default_platform',
    'default_provider',
    'driver',
    'hosts',
    'installed_deps',
    'multiple_platforms',
]


class InvalidState(Exception):
    """
    Exception class raised when an error occurs in :class:`.State`.
    """
    pass


class State(object):
    def __init__(self, state_file='state.yml'):
        """
        Initialize a new state class and returns None.

        :param state_file: An optional string containing the path to the state
        file.
        :returns: None
        """
        self._state_file = state_file
        self._data = self._get_data()
        self._write_state_file()

    def marshal(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._write_state_file()

        return wrapper

    @property
    def converged(self):
        return self._data.get('converged')

    @property
    def created(self):
        return self._data.get('created')

    @property
    def default_platform(self):
        return self._data.get('default_platform')

    @property
    def default_provider(self):
        return self._data.get('default_provider')

    @property
    def driver(self):
        return self._data.get('driver')

    @property
    def hosts(self):
        return self._data.get('hosts')

    @property
    def multiple_platforms(self):
        return self._data.get('multiple_platforms')

    @property
    def installed_deps(self):
        return self._data.get('installed_deps')

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
        if os.path.isfile(self._state_file):
            return self._load_file()
        return self._default_data()

    def _default_data(self):
        return {
            "converged": None,
            "created": None,
            "default_platform": None,
            "default_provider": None,
            "driver": None,
            "hosts": {},
            "multiple_platforms": None
        }

    def _load_file(self):
        with open(self._state_file) as stream:
            return yaml.safe_load(stream)

    def _write_state_file(self):
        util.write_file(
            self._state_file,
            yaml.safe_dump(
                self._data,
                default_flow_style=False,
                explicit_start=True,
                encoding='utf-8'))
