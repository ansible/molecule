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

from __future__ import print_function

import os
import sys
import re

import colorama
import sh

from utilities import print_error
from utilities import print_warning


def check_trailing_cruft(ignore_paths=[], exit=True):
    """
    Recursively finds all files relative to CWD and checks them for trailing whitespace and newlines

    :param ignore_paths: list of paths to ignore during checks
    :return:
    """
    filenames = []
    pruned_filenames = []
    found_error = False
    valid_extensions = ['py', 'yml', 'rb']
    for root, dirs, files in os.walk('.'):
        # gets ./subdirectory/filename
        filenames.extend([os.path.join(root, name) for name in files
                          if name.split(os.extsep)[-1] in valid_extensions])
        # gets ./filename
        filenames.extend([os.path.join(root, name) for name in dirs
                          if name.split(os.extsep)[-1] in valid_extensions])

    # only work on files not in our ignore paths
    for f in filenames:
        f_parts = f.split(os.sep)

        try:
            if f_parts[1] in ignore_paths:
                continue
        except IndexError:
            continue

        # don't add directories
        if os.path.isfile(f):
            pruned_filenames.append(f)

    for filename in pruned_filenames:
        # don't process blank files
        if os.path.getsize(filename) < 1:
            continue

        data = [line for line in open(filename, 'r')]
        newline = trailing_newline(data)
        whitespace = trailing_whitespace(data)

        if newline:
            error = '{}Trailing newline found at the end of {}{}\n'
            print(error.format(colorama.Fore.RED, filename,
                               colorama.Fore.RESET))
            found_error = True

        if whitespace:
            error = '{}Trailing whitespace found in {} on lines: {}{}\n'
            lines = ', '.join(str(x) for x in whitespace)
            print(error.format(colorama.Fore.RED, filename, lines,
                               colorama.Fore.RESET))
            found_error = True

    if exit and found_error:
        sys.exit(1)


def trailing_newline(source):
    """
    Checks last item in source list for a trailing newline

    :param source: list to check for trailing newline
    :return: True if a trailing newline is found, otherwise None
    """
    if re.match(r'^\n$', source[-1]):
        return True
    return


def trailing_whitespace(source):
    """
    Checks each item in source list for a trailing whitespace

    :param source: list of lines to check for trailing whitespace
    :return: List of offending line numbers with trailing whitespace, otherwise None
    """
    lines = []
    for counter, line in enumerate(source):
        l = line.rstrip('\n\r')
        if re.search(r'\s+$', l):
            lines.append(counter + 1)

    return lines if lines else None


def rubocop(serverspec_dir,
            debug=False,
            env=os.environ.copy(),
            pattern='/**/*.rb',
            out=print_warning,
            err=print_error):
    """
    Runs rubocop against specified directory with specified pattern

    :param serverspec_dir: Directory to search for files to lint
    :param debug: Pass debug flag to rubocop
    :param pattern: Search pattern to pass to rubocop
    :param env: Environment to pass to underlying sh call
    :param out: Function to process STDOUT for underlying sh call
    :param err: Function to process STDERR for underlying sh call
    :return: sh response object
    """
    kwargs = {'_env': env, '_out': out, '_err': err, 'debug': debug}

    if 'HOME' not in kwargs['_env']:
        kwargs['_env']['HOME'] = os.path.expanduser('~')

    match = serverspec_dir + pattern
    return sh.rubocop(match, **kwargs)


def rake(rakefile,
         debug=False,
         env=os.environ.copy(),
         out=print_warning,
         err=print_error):
    """
    Runs rake with specified rakefile

    :param rakefile: Path to rakefile
    :param debug: Pass trace flag to rake
    :param env: Environment to pass to underlying sh call
    :param out: Function to process STDOUT for underlying sh call
    :param err: Function to process STDERR for underlying sh call
    :return: sh response object
    """
    kwargs = {'_env': env,
              '_out': out,
              '_err': err,
              'trace': debug,
              'rakefile': rakefile}

    if 'HOME' not in kwargs['_env']:
        kwargs['_env']['HOME'] = os.path.expanduser('~')

    return sh.rake(**kwargs)


def testinfra(testinfra_dir, env=None, debug=False, **kwargs):
    """
    Runs testinfra against specified ansible inventory file

    :param inventory: Path to ansible inventory file
    :param testinfra_dir: Path to the testinfra tests
    :param debug: Pass debug flag to testinfra
    :param env: Environment to pass to underlying sh call
    :param out: Function to process STDOUT for underlying sh call
    :param err: Function to process STDERR for underlying sh call
    :return: sh response object
    """
    kwargs['debug'] = debug
    kwargs['_env'] = env

    if 'HOME' not in kwargs['_env']:
        kwargs['_env']['HOME'] = os.path.expanduser('~')

    tests = '{}/test_*.py'.format(testinfra_dir)
    tests_glob = sh.glob(tests)

    return sh.testinfra(tests_glob, **kwargs)
