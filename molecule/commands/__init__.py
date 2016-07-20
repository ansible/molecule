#  Copyright (c) 2015-2016 Cisco Systems
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

# NOTE: Importing into the ``molecule.commands`` namespace, to prevent
# collisions (e.g. ``list``).  The CLI usage may conflict with reserved words
# or builtins.

from molecule.commands import base  # noqa
from molecule.commands import converge  # noqa
from molecule.commands import create  # noqa
from molecule.commands import destroy  # noqa
from molecule.commands import idempotence  # noqa
from molecule.commands import init  # noqa
from molecule.commands import list  # noqa
from molecule.commands import login  # noqa
from molecule.commands import status  # noqa
from molecule.commands import syntax  # noqa
from molecule.commands import test  # noqa
from molecule.commands import verify  # noqa
