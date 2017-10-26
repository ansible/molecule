#  Copyright (c) 2015-2017 Cisco Systems, Inc.

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

from __future__ import absolute_import

from molecule import logger

LOG = logger.get_logger(__name__)


class AnsiblePlaybooks(object):
    """ A class to act as a module to namespace playbook properties. """

    def __init__(self, config):
        """
        Initialize a new namespace class and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        self._config = config

    @property
    def create(self):
        return self._get_ansible_playbook('create')

    @property
    def converge(self):
        c = self._config.config

        return self._config.provisioner.get_abs_path(
            c['provisioner']['playbooks']['converge'])

    @property
    def destroy(self):
        return self._get_ansible_playbook('destroy')

    @property
    def prepare(self):
        return self._get_ansible_playbook('prepare')

    @property
    def side_effect(self):
        return self._get_ansible_playbook('side_effect')

    def _get_ansible_playbook(self, section):
        c = self._config.config
        driver_dict = c['provisioner']['playbooks'].get(
            self._config.driver.name)

        if driver_dict:
            try:
                playbook = driver_dict[section]
            except KeyError:
                playbook = c['provisioner']['playbooks'][section]
        else:
            playbook = c['provisioner']['playbooks'][section]

        if playbook is not None:
            return self._config.provisioner.get_abs_path(playbook)
        return
