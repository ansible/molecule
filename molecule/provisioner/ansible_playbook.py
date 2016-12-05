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

import sh

from molecule import util


class AnsiblePlaybook(object):
    def __init__(self, playbook, inventory, config):
        """
        Sets up the requirements to execute `ansible-playbook` and returns
        None.

        :param playbook: A string containing the path to the playbook.
        :param inventory: A string containing the path to the inventory.
        :param config: An instance of a Molecule config.
        :returns: None
        """
        self._ansible_playbook_command = None
        self._playbook = playbook
        self._inventory = inventory
        self._config = config

    def bake(self):
        """
        Bake an `ansible-playbook` command so it's ready to execute and returns
        None.

        :return: None
        """
        options = {'inventory': self._inventory}
        self._ansible_playbook_command = sh.ansible_playbook.bake(
            options,
            self._playbook,
            _out=util.callback_info,
            _err=util.callback_error)

    def execute(self):
        """
        Executes `ansible-playbook` and returns None.

        :return: None
        """
        if self._ansible_playbook_command is None:
            self.bake()

        try:
            util.run_command(
                self._ansible_playbook_command,
                debug=self._config.args.get('debug'))
        except sh.ErrorReturnCode as e:
            util.sysexit(e.exit_code)
