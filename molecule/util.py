#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

from __future__ import print_function

import fnmatch
import os
import re
import sys

import colorama
import yaml

colorama.init(autoreset=True)


def print_success(msg):
    template = '{}{{}}'.format(colorama.Fore.GREEN)
    print_msg(template, msg)


def print_info(msg, pretty=True):
    if pretty:
        template = '--> {}{{}}'.format(colorama.Fore.CYAN)
    else:
        template = '    {}'
    print_msg(template, msg)


def print_warn(msg):
    template = '{}{{}}'.format(colorama.Fore.YELLOW)
    print_msg(template, msg)


def print_error(msg, pretty=True):
    color = colorama.Fore.RED
    if pretty:
        template = '{}ERROR: {{}}'.format(color)
    else:
        template = '{}{{}}'.format(color)
    print_msg(template, msg, file=sys.stderr)


def print_msg(template, msg, **kwargs):
    print(template.format(msg.rstrip()), **kwargs)


def print_debug(title, data):
    print(''.join([
        colorama.Back.WHITE, colorama.Style.BRIGHT, colorama.Fore.BLACK,
        'DEBUG: ' + title, colorama.Fore.RESET, colorama.Back.RESET,
        colorama.Style.RESET_ALL
    ]))
    print(''.join([
        colorama.Fore.BLACK, colorama.Style.BRIGHT, data,
        colorama.Style.RESET_ALL, colorama.Fore.RESET
    ]))


def callback_info(msg):
    """ A `print_info` wrapper to stream `sh` modules stdout. """
    print_info(msg, pretty=False)


def callback_error(msg):
    """ A `print_error` wrapper to stream `sh` modules stderr. """
    print_error(msg, pretty=False)


def sysexit(code=1):
    sys.exit(code)


def sysexit_with_message(msg, code=1):
    print_error(msg)
    sysexit(code)


def run_command(cmd, debug=False):
    """
    Execute the given command and returns None.
    :param cmd: A `sh.Command` object to execute.
    :param debug: An optional bool to toggle debug output.
    :return: ``sh`` object
    """
    if debug:
        print_debug('COMMAND', str(cmd))
    return cmd()


def os_walk(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)

                yield filename


def write_file(filename, content):
    """
    Writes a file with the given filename and content and returns None.

    :param filename: A string containing the target filename.
    :param content: A string containing the data to be written.
    :return: None
    """
    with open(filename, 'w') as f:
        f.write(content)

    file_prepender(filename)


def file_prepender(filename):
    """
    Prepend an informational header on files managed by Molecule and returns
    None.

    :param filename: A string containing the target filename.
    :return: None
    """
    molecule_header = '# Molecule managed\n\n'
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(molecule_header + content)


def safe_dump(data):
    """
    Dump the provided data to a YAML document and returns a string.

    :param data: A string containing an absolute path to the file to parse.
    :return: str
    """
    # TODO(retr0h): Do we need to encode?
    # yaml.dump(data) produces the document as a str object in both python
    # 2 and 3.
    return yaml.safe_dump(data, default_flow_style=False, explicit_start=True)


def safe_load(string):
    """
    Parse the provided string returns a dict.

    :param string: A string to be parsed.
    :return: dict
    """
    return yaml.safe_load(string) or {}


def safe_load_file(filename):
    """
    Parse the provided YAML file and returns a dict.

    :param filename: A string containing an absolute path to the file to parse.
    :return: dict
    """
    with open(filename, 'r') as stream:
        return safe_load(stream)


def instance_with_scenario_name(instance_name, scenario_name):
    return '{}-{}'.format(instance_name, scenario_name)


def ansi_escape(string):
    return re.sub(r'\x1b[^m]*m', '', string)
