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
import sh

from utilities import print_stderr
from utilities import print_stdout


def rake(rakefile, debug=False, env=os.environ.copy(), out=print_stdout, err=print_stderr):
    """
    Runs rake with specified rakefile

    :param rakefile: Path to rakefile
    :param debug: Pass trace flag to rake
    :param env: Environment to pass to underlying sh call
    :param out: Function to process STDOUT for underlying sh call
    :param err: Function to process STDERR for underlying sh call
    :return: sh response object
    """
    kwargs = {'_env': env, '_out': out, '_err': err, 'trace': debug, 'rakefile': rakefile}

    if 'HOME' not in kwargs['_env']:
        kwargs['_env']['HOME'] = os.path.expanduser('~')

    return sh.rake(**kwargs)


def testinfra(inventory, testinfra_dir, debug=False, env=None, out=print_stdout, err=print_stderr):
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
    kwargs = {
        '_env': env,
        '_out': out,
        '_err': err,
        'debug': debug,
        'ansible_inventory': inventory,
        'sudo': True,
        'connection': 'ansible'
    }

    if 'HOME' not in kwargs['_env']:
        kwargs['_env']['HOME'] = os.path.expanduser('~')

    return sh.testinfra(testinfra_dir, **kwargs)
