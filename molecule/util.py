#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

import cookiecutter
import cookiecutter.main

import os
import sys

import colorama
import jinja2

colorama.init(autoreset=True)


def print_success(msg):
    template = '{}{{}}'.format(colorama.Fore.GREEN)
    print_msg(template, msg)


def print_info(msg, pretty=True):
    if pretty:
        msg = msg.replace('\n', '\n    ')
        template = '--> {}{{}}'.format(colorama.Fore.RESET)
        print_msg(template, msg)
    else:
        print_msg('{}', msg)


def print_debug(title, data):
    data = data.replace('\n', '\n       ')
    print(''.join([
        colorama.Back.WHITE, colorama.Style.BRIGHT, colorama.Fore.BLACK,
        'DEBUG: ' + title, colorama.Fore.RESET, colorama.Back.RESET,
        colorama.Style.RESET_ALL
    ]))
    print(''.join([
        colorama.Fore.BLACK, colorama.Style.BRIGHT, data,
        colorama.Style.RESET_ALL, colorama.Fore.RESET
    ]))


def print_warn(msg):
    template = '{}{{}}'.format(colorama.Fore.YELLOW)
    print_msg(template, msg)


def print_error(msg, pretty=True):
    color = colorama.Fore.RED
    template = '{}{{}}'.format(color)
    msg = msg.replace('\n', '\n       ')

    if pretty:
        template = '{}ERROR: {{}}'.format(color)

    print_msg(template, msg, file=sys.stderr)


def print_msg(template, msg, **kwargs):
    print(template.format(msg.rstrip()), **kwargs)


def callback_info(msg):
    """ A `print_info` wrapper to stream `sh` modules stdout. """
    print_info(msg, pretty=False)


def callback_error(msg):
    """ A `print_error` wrapper to stream `sh` modules stderr. """
    print_error(msg, pretty=False)


def write_template(src, dest, kwargs={}, _module='molecule', _dir='template'):
    """
    Writes a file from a jinja2 template and returns None.

    :param src: A string containing the the target template files to use.
    :param dest: A string containing the destination of the templatized file to
     be written.
    :param kwargs: A dict of arguments passed to jinja2 when rendering
     template.
    :param _module: An optional module (to look for template files) passed to
     jinja2 PackageLoader.
    :param _dir: An optional directory (to look for template files) passed to
     jinja2 PackageLoader
    :return: None
    """
    src = os.path.expanduser(src)
    path = os.path.dirname(src)
    filename = os.path.basename(src)

    # template file doesn't exist
    if path and not os.path.isfile(src):
        msg = 'Unable to locate template file: {}'.format(src)
        print_error(msg)
        sysexit()

    # look for template in filesystem, then molecule package
    loader = jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(
            path, followlinks=True), jinja2.PackageLoader(_module, _dir)
    ])

    env = jinja2.Environment(loader=loader)
    template = env.get_template(filename)

    with open(dest, 'w') as f:
        f.write(template.render(**kwargs))


def process_templates(template_dir, extra_context, output_dir, overwrite=True):
    """
    Process templates as found in the named directory.

    :param template_dir: An absolute or relative path to a directory where the
     templates are located. If the provided directory is a relative path, it
     is resolved using a known location.
    :type template_dir: str
    :param extra_context: A set of values that are used to override default
     or user specified values.
    :type extra_context: dict or None
    :param output_dir: An absolute path to a directory where the templates
     should be written to.
    :type output_dir: str
    :param overwrite: Whether or not to overwrite existing templates.
     Defaults to True.
    :type overwrite: bool
    :return: None
    """

    template_dir = _resolve_template_dir(template_dir)

    cookiecutter.main.cookiecutter(
        template_dir,
        extra_context=extra_context,
        output_dir=output_dir,
        overwrite_if_exists=overwrite,
        no_input=True, )


def _resolve_template_dir(template_dir):
    if not os.path.isabs(template_dir):
        template_dir = os.path.join(
            os.path.dirname(__file__), 'cookiecutter', template_dir)

    return template_dir


def write_file(filename, content):
    """
    Writes a file with the given filename and content and returns None.

    :param filename: A string containing the target filename.
    :param content: A string containing the data to be written.
    :return: None
    """
    with open(filename, 'w') as f:
        f.write(content)


def format_instance_name(name, platform, instances):
    """
    Takes an instance name and formats it according to options specified in the
    instance's config and returns a string.

    :param name: A string containg the name of the instance.
    :param platform: A string containing the current molecule platform in use.
    :param instances: A dict containing the instance data.
    :return: str if found, otherwise None.
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
        return name

    # add platform to name
    if working_instance['options'].get('append_platform_to_hostname'):
        if platform and platform != 'all':
            return name + '-' + platform

    # if we fall through, return the default name
    return name


def sysexit(code=1):
    sys.exit(code)


def run_command(cmd, debug=False):
    """
    Execute the given command and return None.

    :param cmd: A `sh.Command` object to execute.
    :param debug: An optional bool to toggle debug output.
    :return: ``sh`` object
    """
    if debug:
        print_debug('COMMAND', str(cmd))
    return cmd()
