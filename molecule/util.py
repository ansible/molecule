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

from __future__ import print_function

import contextlib
import fnmatch
import jinja2
import os
import re
import sys

import colorama
import yaml

from molecule import logger

LOG = logger.get_logger(__name__)

colorama.init(autoreset=True)


class SafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(SafeDumper, self).increase_indent(flow, False)


def print_debug(title, data):
    title = 'DEBUG: {}'.format(title)
    title = [
        colorama.Back.WHITE, colorama.Style.BRIGHT, colorama.Fore.BLACK, title,
        colorama.Fore.RESET, colorama.Back.RESET, colorama.Style.RESET_ALL
    ]
    print(''.join(title))
    data = [
        colorama.Fore.BLACK, colorama.Style.BRIGHT, data,
        colorama.Style.RESET_ALL, colorama.Fore.RESET
    ]
    print(''.join(data))


def print_environment_vars(env):
    """
    Print ``Ansible`` and ``Molecule`` environment variables and returns None.

    :param env: A dict containing the shell's environment as collected by
    ``os.environ``.
    :return: None
    """
    ansible_env = {k: v for (k, v) in env.items() if 'ANSIBLE_' in k}
    print_debug('ANSIBLE ENVIRONMENT', safe_dump(ansible_env))

    molecule_env = {k: v for (k, v) in env.items() if 'MOLECULE_' in k}
    print_debug('MOLECULE ENVIRONMENT', safe_dump(molecule_env))

    combined_env = ansible_env.copy()
    combined_env.update(molecule_env)
    print_debug('SHELL REPLAY', " ".join(
        ["{}={}".format(k, v) for (k, v) in sorted(combined_env.items())]))
    print()


def sysexit(code=1):
    sys.exit(code)


def sysexit_with_message(msg, code=1):
    LOG.critical(msg)
    sysexit(code)


def run_command(cmd, debug=False):
    """
    Execute the given command and returns None.

    :param cmd: A `sh.Command` object to execute.
    :param debug: An optional bool to toggle debug output.
    :return: ``sh`` object
    """
    if debug:
        # WARN(retr0h): Uses an internal ``sh`` data structure to dig
        # the environment out of the ``sh.command`` object.
        print_environment_vars(cmd._partial_call_args.get('env', {}))
        print_debug('COMMAND', str(cmd))
        print()
    return cmd()


def os_walk(directory, pattern, excludes=[]):
    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if d not in excludes]
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)

                yield filename


def render_template(template, **kwargs):
    t = jinja2.Environment()
    t = t.from_string(template)

    return t.render(kwargs)


def write_file(filename, content):
    """
    Writes a file with the given filename and content and returns None.

    :param filename: A string containing the target filename.
    :param content: A string containing the data to be written.
    :return: None
    """
    with open_file(filename, 'w') as f:
        f.write(content)

    file_prepender(filename)


def molecule_prepender(content):
    return '# Molecule managed\n\n' + content


def file_prepender(filename):
    """
    Prepend an informational header on files managed by Molecule and returns
    None.

    :param filename: A string containing the target filename.
    :return: None
    """
    with open_file(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(molecule_prepender(content))


def safe_dump(data):
    """
    Dump the provided data to a YAML document and returns a string.

    :param data: A string containing an absolute path to the file to parse.
    :return: str
    """
    # TODO(retr0h): Do we need to encode?
    # yaml.dump(data) produces the document as a str object in both python
    # 2 and 3.
    return yaml.dump(
        data, Dumper=SafeDumper, default_flow_style=False, explicit_start=True)


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
    with open_file(filename) as stream:
        return safe_load(stream)


@contextlib.contextmanager
def open_file(filename, mode='r'):
    """
    Open the provide file safely and returns a file type.

    :param filename: A string containing an absolute path to the file to open.
    :param mode: A string describing the way in which the file will be used.
    :return: file type
    """
    with open(filename, mode) as stream:
        yield stream


def instance_with_scenario_name(instance_name, scenario_name):
    return '{}-{}'.format(instance_name, scenario_name)


def strip_ansi_escape(string):
    return re.sub(r'\x1b[^m]*m', '', string)


def strip_ansi_color(s):
    # Taken from tabulate
    invisible_codes = re.compile('\x1b\[\d*m')

    return re.sub(invisible_codes, '', s)


def verbose_flag(options):
    verbose = 'v'
    verbose_flag = []
    for i in range(0, 3):
        if options.get(verbose):
            verbose_flag = ['-{}'.format(verbose)]
            del options[verbose]
            if options.get('verbose'):
                del options['verbose']
            break
        verbose = verbose + 'v'

    return verbose_flag


def title(word):
    return ' '.join(x.capitalize() or '_' for x in word.split('_'))


def exit_with_invalid_section(section, name):
    msg = "Invalid {} named '{}' configured.".format(section, name)
    sysexit_with_message(msg)


def abs_path(path):
    return os.path.abspath(path)


def camelize(string):
    # NOTE(retr0h): Taken from jpvanhal/inflection
    # https://github.com/jpvanhal/inflection
    return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), string)


def underscore(string):
    # NOTE(retr0h): Taken from jpvanhal/inflection
    # https://github.com/jpvanhal/inflection
    string = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', string)
    string = re.sub(r"([a-z\d])([A-Z])", r'\1_\2', string)
    string = string.replace("-", "_")

    return string.lower()
