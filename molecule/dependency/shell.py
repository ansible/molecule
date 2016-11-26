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


class Shell(object):
    def __init__(self,
                 config,
                 _env=None,
                 _out=util.callback_info,
                 _err=util.callback_error,
                 debug=False):
        """
        Sets up requirements via a command and returns None.

        :param config: A molecule config object.
        :param _env: An optional environment to pass to underlying :func:`sh`
         call.
        :param _out: An optional function to process STDOUT for underlying
         :func:`sh` call.
        :param _err: An optional function to process STDERR for underlying
         :func:`sh` call.
        :param debug: An optional bool to toggle debug output.
        :return: None
        """
        self._config = config
        self._command = None
        self._env = _env if _env else os.environ.copy()
        self._out = _out
        self._err = _err
        self._debug = debug

    def bake(self):
        """
        Bake shell command so it's ready to execute and returns None.

        :return: None
        """
        command = self._config['dependency']['command'].split(' ')
        self._command = getattr(sh, command.pop(0))
        self._command = self._command.bake(command)
        self._command = self._command.bake(
            _env=self._env, _out=self._out, _err=self._err)

    def execute(self):
        """
        Executes shell command and returns the command's stdout.

        :return: The command's output, otherwise sys.exit on command failure.
        """

        if self._command is None:
            self.bake()

        try:
            return util.run_command(self._command, debug=self._debug).stdout
        except sh.ErrorReturnCode as e:
            util.print_error(str(e))
            util.sysexit(e.exit_code)
