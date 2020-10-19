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
"""Base Ansible Galaxy dependency module."""

import abc
import copy
import os

import sh

from molecule import logger, util
from molecule.dependency import base

LOG = logger.get_logger(__name__)


class AnsibleGalaxyBase(base.Base):
    """Ansible Galaxy dependency base class."""

    __metaclass__ = abc.ABCMeta

    FILTER_OPTS = ()

    def __init__(self, config):
        """Construct AnsibleGalaxy."""
        super(AnsibleGalaxyBase, self).__init__(config)
        self._sh_command = None

        self.command = "ansible-galaxy"

    @abc.abstractproperty
    def install_path(self):  # noqa cover
        pass

    @abc.abstractproperty
    def requirements_file(self):  # noqa cover
        pass

    @property
    def default_options(self):
        d = {
            "force": True,
        }
        if self._config.debug:
            d["vvv"] = True

        return d

    def filter_options(self, opts, keys):
        """
        Filter certain keys from a dictionary.

        Removes all the values of ``keys`` from the dictionary ``opts``, if
        they are present. Returns the resulting dictionary. Does not modify the
        existing one.

        :return: A copy of ``opts`` without the value of keys
        """
        c = copy.copy(opts)
        for key in keys:
            if key in c.keys():
                del c[key]
        return c

    # NOTE(retr0h): Override the base classes' options() to handle
    # ``ansible-galaxy`` one-off.
    @property
    def options(self):
        o = self._config.config["dependency"]["options"]
        # NOTE(retr0h): Remove verbose options added by the user while in
        # debug.
        if self._config.debug:
            o = util.filter_verbose_permutation(o)

        o = util.merge_dicts(self.default_options, o)
        return self.filter_options(o, self.FILTER_OPTS)

    @property
    def default_env(self):
        return util.merge_dicts(os.environ, self._config.env)

    def bake(self):
        """
        Bake an ``ansible-galaxy`` command so it's ready to execute and returns \
        None.

        :return: None
        """
        options = self.options
        verbose_flag = util.verbose_flag(options)

        self._sh_command = getattr(sh, self.command)
        self._sh_command = self._sh_command.bake(*self.COMMANDS)
        self._sh_command = self._sh_command.bake(
            options, *verbose_flag, _env=self.env, _out=LOG.out, _err=LOG.error
        )

    def execute(self):
        if not self.enabled:
            msg = "Skipping, dependency is disabled."
            LOG.warning(msg)
            return

        if not self._has_requirements_file():
            msg = "Skipping, missing the requirements file."
            LOG.warning(msg)
            return

        if self._sh_command is None:
            self.bake()

        self._setup()
        self.execute_with_retries()

    def _setup(self):
        """
        Prepare the system for using ``ansible-galaxy`` and returns None.

        :return: None
        """
        if not os.path.isdir(self.install_path):
            os.makedirs(self.install_path)

    def _has_requirements_file(self):
        return os.path.isfile(self.requirements_file)
