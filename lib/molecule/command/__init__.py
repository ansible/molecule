# noqa D104
#
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

# NOTE(retr0h): Importing into the ``molecule.command`` namespace, to prevent
# collisions (e.g. ``list``).  The CLI usage may conflict with reserved words
# or builtins.

from molecule.command import base  # noqa
from molecule.command import check  # noqa
from molecule.command import cleanup  # noqa
from molecule.command import converge  # noqa
from molecule.command import create  # noqa
from molecule.command import dependency  # noqa
from molecule.command import destroy  # noqa
from molecule.command import drivers  # noqa
from molecule.command import idempotence  # noqa
from molecule.command import lint  # noqa
from molecule.command import list  # noqa
from molecule.command import login  # noqa
from molecule.command import matrix  # noqa
from molecule.command import prepare  # noqa
from molecule.command import reset  # noqa
from molecule.command import side_effect  # noqa
from molecule.command import syntax  # noqa
from molecule.command import test  # noqa
from molecule.command import verify  # noqa
from molecule.command.init import init  # noqa
