# noqa: D104
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
from __future__ import annotations

from molecule.command import (
    base,  # noqa: F401
    check,  # noqa: F401
    cleanup,  # noqa: F401
    converge,  # noqa: F401
    create,  # noqa: F401
    dependency,  # noqa: F401
    destroy,  # noqa: F401
    drivers,  # noqa: F401
    idempotence,  # noqa: F401
    list,  # noqa: A004, F401
    login,  # noqa: F401
    matrix,  # noqa: F401
    prepare,  # noqa: F401
    reset,  # noqa: F401
    side_effect,  # noqa: F401
    syntax,  # noqa: F401
    test,  # noqa: F401
    verify,  # noqa: F401
)
from molecule.command.init import init  # noqa: F401
