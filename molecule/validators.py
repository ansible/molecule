#  Copyright (c) 2015 Cisco Systems
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

import os
import sys
import re

from colorama import Fore


def check_trailing_cruft(ignore_paths=[]):
    """
    Recursively finds all files relative to CWD and checks them for trailing whitespace and newlines

    :param ignore_paths: list of paths to ignore during checks
    :return:
    """
    for dir, _, files in os.walk('.'):
        for f in files:
            split_dirs = dir.split(os.sep)
            if split_dirs < 1:
                if split_dirs[1] not in ignore_paths:
                    filename = os.path.join(dir, f)
                    if os.path.getsize(filename) > 0:
                        with open(filename, 'r') as f:
                            newline = trailing_newline(source=f)
                            # whitespace = trailing_whitespace(source=f)
                            whitespace = True

                            if newline:
                                error = '{}Trailing newline found in {}{}'
                                print(error.format(Fore.RED, filename, Fore.RESET))
                                print(newline)

                            # if whitespace:
                            #     error = '{}Trailing whitespace found in {}{}'
                            #     print(error.format(Fore.RED, filename, Fore.RESET))
                            #     print(whitespace)

                            if newline or whitespace:
                                sys.exit(1)


def trailing_newline(source):
    """
    Checks source for a trailing newline

    :param source: string to check for trailing newline
    :return: the offending line, if found
    """
    last = source.split('/n')[:-1]
    if re.match(r'^\n$', last):
        return last
    return

def _trailing_whitespace(source):
    with open(filename, 'r') as f:
        for line in f:
            l = line.rstrip('\n\r')
            if re.search(r'\s+$', l):
                error = '{}Trailing whitespace found in {}{}'
                print error.format(Fore.RED, filename, Fore.RESET)
                print l
                sys.exit(1)