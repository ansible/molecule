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

import copy
import os
import sys

from colorama import Fore
from jinja2 import Environment
from jinja2 import ChoiceLoader
from jinja2 import FileSystemLoader
from jinja2 import PackageLoader


def merge_dicts(a, b, raise_conflicts=False, path=None):
    """
    Merges the values of B into A.
    If the raise_conflicts flag is set to True, a LookupError will be raised if the keys are conflicting.
    :param a: the target dictionary
    :param b: the dictionary to import
    :param raise_conflicts: flag to raise an exception if two keys are colliding
    :param path: the dictionary path. Used to show where the keys are conflicting when an exception is raised.
    :return: The dictionary A with the values of the dictionary B merged into it.
    """
    # Set path.
    if path is None:
        path = []

    # Go through the keys of the 2 dictionaries.
    for key in b:
        # If the key exist in both dictionary, check whether we must update or not.
        if key in a:
            # Dig deeper for keys that have dictionary values.
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], raise_conflicts=raise_conflicts, path=(path + [str(key)]))

            # Skip the identical values.
            elif a[key] == b[key]:
                pass
            else:
                # Otherwise raise an error if the same keys have different values.
                if raise_conflicts:
                    raise LookupError("Conflict at '{path}'".format(path='.'.join(path + [str(key)])))

                # Or replace the value of A with the value of B.
                a[key] = b[key]
        else:
            # If the key does not exist in A, import it.
            a[key] = copy.deepcopy(b[key]) if isinstance(b[key], dict) else b[key]

    return a


def write_template(src, dest, kwargs={}, _module='molecule', _dir='templates'):
    """
    Writes a file from a jinja2 template
    :param src: the target template files to use
    :param dest: destination of the templatized file to be written
    :param kwargs: dictionary of arguments passed to jinja2 when rendering template
    :param _module: module (to look for template files) passed to jinja2 PackageLoader
    :param _dir: directory (to look for template files) passed to jinja2 PackageLoader
    :return: None
    """
    path = os.path.dirname(src)
    filename = os.path.basename(src)

    # template file doesn't exist
    if path and not os.path.isfile(src):
        print('\n{}Unable to locate template file: {}{}'.format(Fore.RED, src, Fore.RESET))
        sys.exit(1)

    # look for template in filesystem, them molecule package
    loader = ChoiceLoader([FileSystemLoader(path, followlinks=True), PackageLoader(_module, _dir)])

    env = Environment(loader=loader)
    template = env.get_template(filename)

    with open(dest, 'w') as f:
        f.write(template.render(**kwargs))


def write_file(filename, content):
    """
    Writes a file with the given filename using the given content. Overwrites, does not append.
    :param filename: the target filename
    :param content: what gets written into the file
    :return: None
    """
    with open(filename, 'w') as f:
        f.write(content)


def format_instance_name(name, platform, instances):
    """
    Takes an instance name and formats it according to options specified in the instance's config
    :param name: the name of the instance
    :param platform: the current molecule platform in use
    :param instances: the current molecule instances dict in use
    :return: formatted instance name if found in instances, otherwise None
    """
    working_instance = None

    # search instances for given name
    for instance in instances:
        if instance['name'] == name:
            working_instance = instance
            break

    # no instance found with given name
    if working_instance is None:
        return

    # return the default name if no options are specified for instance
    if working_instance.get('options') is None:
        return name + '-' + platform

    # don't add platform to name
    if working_instance['options'].get('append_platform_to_hostname') is False:
        return name

    # if we fall through, return the default name
    return name + '-' + platform


def print_stdout(line):
    """
    Prints a line to stdout without a \n at the end.
    :param line: what gets printed
    :return: None
    """
    print(line, file=sys.stdout, end='')
    sys.stdout.flush()


def print_stderr(line):
    """
    Prints a line to stderr without a \n at the end.
    :param line: what gets printed
    :return: None
    """
    print(line, file=sys.stderr, end='')
    sys.stderr.flush()
