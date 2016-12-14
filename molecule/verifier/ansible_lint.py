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

import os

import sh

from molecule import util
from molecule.verifier import base


class AnsibleLint(base.Base):
    """
    This is likely to be the source of issues.  The class was implemented to
    bring standardization to roles managed by molecule.  How we further refine
    this class, and its usage is up for discussion.
    """

    def __init__(self, molecule):
        super(AnsibleLint, self).__init__(molecule)
        self._playbook = molecule.config.config['ansible']['playbook']
        self._ignore_paths = molecule.config.config['molecule']['ignore_paths']
        self._debug = molecule.args.get('debug')

    def execute(self):
        """
        Executes ansible-lint against the configured playbook and returns
        None.

        :return: None
        """
        env = {
            'ANSIBLE_CONFIG':
            self._molecule.config.config['ansible']['config_file'],
            'PYTHONPATH': os.environ.get('PYTHONPATH'),
            'HOME': os.environ.get('HOME')
        }

        if 'ansible_lint' not in self._molecule.disabled:
            msg = 'Executing ansible-lint...'
            util.print_info(msg)
            args = [self._playbook]
            [args.extend(["--exclude", path]) for path in self._ignore_paths]
            cmd = sh.ansible_lint.bake(
                *args,
                _env=env,
                _out=util.callback_info,
                _err=util.callback_error)
            util.run_command(cmd, debug=self._debug)
