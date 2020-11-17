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
"""Base class used by init command."""

import abc
import os

import cookiecutter
import cookiecutter.main

from molecule import logger, util

LOG = logger.get_logger(__name__)


class Base(object):
    """Init Command Base Class."""

    __metaclass__ = abc.ABCMeta

    def _process_templates(
        self, template_dir, extra_context, output_dir, overwrite=True
    ):
        """
        Process templates as found in the named directory.

        :param template_dir: A string containing an absolute or relative path
         to a directory where the templates are located. If the provided
         directory is a relative path, it is resolved using a known location.
        :param extra_context: A dict of values that are used to override
         default or user specified values.
        :param output_dir: An string with an absolute path to a directory where
         the templates should be written to.
        :param overwrite: An optional bool whether or not to overwrite existing
         templates.
        :return: None
        """
        template_dir = self._resolve_template_dir(template_dir)
        self._validate_template_dir(template_dir)

        try:
            cookiecutter.main.cookiecutter(
                template_dir,
                extra_context=extra_context,
                output_dir=output_dir,
                overwrite_if_exists=overwrite,
                no_input=True,
            )
        except cookiecutter.exceptions.NonTemplatedInputDirException:
            util.sysexit_with_message(
                "The specified template directory ("
                + str(template_dir)
                + ") is in an invalid format"
            )

    def _resolve_template_dir(self, template_dir):
        if not os.path.isabs(template_dir):
            template_dir = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    os.path.pardir,
                    os.path.pardir,
                    "cookiecutter",
                    template_dir,
                )
            )

        return template_dir

    def _validate_template_dir(self, template_dir):
        if not os.path.isdir(template_dir):
            util.sysexit_with_message(
                "The specified template directory ("
                + str(template_dir)
                + ") does not exist"
            )
