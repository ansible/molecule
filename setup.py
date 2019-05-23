#! /usr/bin/env python
#  Copyright (c) 2019 Red Hat, Inc.
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
"""Molecule distribution package setuptools installer."""

import setuptools

HAS_DIST_INFO_CMD = False
try:
    import setuptools.command.dist_info
    HAS_DIST_INFO_CMD = True
except ImportError:
    """Setuptools version is too old."""


ALL_STRING_TYPES = tuple(map(type, ('', b'', u'')))
MIN_NATIVE_SETUPTOOLS_VERSION = 34, 4, 0
"""Minimal setuptools having good read_configuration implementation."""

RUNTIME_SETUPTOOLS_VERSION = tuple(map(int, setuptools.__version__.split('.')))
"""Setuptools imported now."""

READ_CONFIG_SHIM_NEEDED = (
    RUNTIME_SETUPTOOLS_VERSION < MIN_NATIVE_SETUPTOOLS_VERSION
)


def str_if_nested_or_str(s):
    """Turn input into a native string if possible."""
    if isinstance(s, ALL_STRING_TYPES):
        return str(s)
    if isinstance(s, (list, tuple)):
        return type(s)(map(str_if_nested_or_str, s))
    if isinstance(s, (dict, )):
        return stringify_dict_contents(s)
    return s


def stringify_dict_contents(dct):
    """Turn dict keys and values into native strings."""
    return {
        str_if_nested_or_str(k): str_if_nested_or_str(v)
        for k, v in dct.items()
    }


if not READ_CONFIG_SHIM_NEEDED:
    from setuptools.config import read_configuration, ConfigOptionsHandler
    import setuptools.config
    import setuptools.dist

    # Set default value for 'use_scm_version'
    setattr(setuptools.dist.Distribution, 'use_scm_version', False)

    # Attach bool parser to 'use_scm_version' option
    class ShimConfigOptionsHandler(ConfigOptionsHandler):
        """Extension class for ConfigOptionsHandler."""

        @property
        def parsers(self):
            """Return an option mapping with default data type parsers."""
            _orig_parsers = super(ShimConfigOptionsHandler, self).parsers
            return dict(use_scm_version=self._parse_bool, **_orig_parsers)

        def parse_section_packages__find(self, section_options):
            find_kwargs = super(
                ShimConfigOptionsHandler, self
            ).parse_section_packages__find(section_options)
            return stringify_dict_contents(find_kwargs)

    setuptools.config.ConfigOptionsHandler = ShimConfigOptionsHandler
else:
    """This is a shim for setuptools<required."""
    import functools
    import io
    import json
    import sys
    import warnings

    try:
        import setuptools.config

        def filter_out_unknown_section(i):
            def chi(self, *args, **kwargs):
                i(self, *args, **kwargs)
                self.sections = {
                    s: v for s, v in self.sections.items()
                    if s != 'packages.find'
                }
            return chi

        setuptools.config.ConfigHandler.__init__ = filter_out_unknown_section(
            setuptools.config.ConfigHandler.__init__,
        )
    except ImportError:
        pass

    def ignore_unknown_options(s):
        @functools.wraps(s)
        def sw(**attrs):
            try:
                ignore_warning_regex = (
                    r"Unknown distribution option: "
                    r"'(license_file|project_urls|python_requires)'"
                )
                warnings.filterwarnings(
                    'ignore',
                    message=ignore_warning_regex,
                    category=UserWarning,
                    module='distutils.dist',
                )
                return s(**attrs)
            finally:
                warnings.resetwarnings()
        return sw

    def parse_predicates(python_requires):
        import itertools
        import operator
        sorted_operators_map = tuple(sorted(
            {
                '>': operator.gt,
                '<': operator.lt,
                '>=': operator.ge,
                '<=': operator.le,
                '==': operator.eq,
                '!=': operator.ne,
                '': operator.eq,
            }.items(),
            key=lambda i: len(i[0]),
            reverse=True,
        ))

        def is_decimal(s):
            return type(u'')(s).isdecimal()

        conditions = map(str.strip, python_requires.split(','))
        for c in conditions:
            for op_sign, op_func in sorted_operators_map:
                if not c.startswith(op_sign):
                    continue
                raw_ver = itertools.takewhile(
                    is_decimal,
                    c[len(op_sign):].strip().split('.'),
                )
                ver = tuple(map(int, raw_ver))
                yield op_func, ver
                break

    def validate_required_python_or_fail(python_requires=None):
        if python_requires is None:
            return

        python_version = sys.version_info
        preds = parse_predicates(python_requires)
        for op, v in preds:
            py_ver_slug = python_version[:max(len(v), 3)]
            condition_matches = op(py_ver_slug, v)
            if not condition_matches:
                raise RuntimeError(
                    "requires Python '{}' but the running Python is {}".
                    format(
                        python_requires,
                        '.'.join(map(str, python_version[:3])),
                    )
                )

    def verify_required_python_runtime(s):
        @functools.wraps(s)
        def sw(**attrs):
            try:
                validate_required_python_or_fail(attrs.get('python_requires'))
            except RuntimeError as re:
                sys.exit('{} {!s}'.format(attrs['name'], re))
            return s(**attrs)
        return sw

    setuptools.setup = ignore_unknown_options(setuptools.setup)
    setuptools.setup = verify_required_python_runtime(setuptools.setup)

    try:
        from configparser import ConfigParser, NoSectionError
    except ImportError:
        from ConfigParser import ConfigParser, NoSectionError
        ConfigParser.read_file = ConfigParser.readfp

    def maybe_read_files(d):
        """Read files if the string starts with `file:` marker."""
        FILE_FUNC_MARKER = 'file:'

        d = d.strip()
        if not d.startswith(FILE_FUNC_MARKER):
            return d
        descs = []
        for fname in map(str.strip, str(d[len(FILE_FUNC_MARKER):]).split(',')):
            with io.open(fname, encoding='utf-8') as f:
                descs.append(f.read())
        return ''.join(descs)

    def cfg_val_to_list(v):
        """Turn config val to list and filter out empty lines."""
        return list(filter(bool, map(str.strip, str(v).strip().splitlines())))

    def cfg_val_to_dict(v):
        """Turn config val to dict and filter out empty lines."""
        return dict(
            map(lambda l: list(map(str.strip, l.split('=', 1))),
                filter(bool, map(str.strip, str(v).strip().splitlines())))
        )

    def cfg_val_to_primitive(v):
        """Parse primitive config val to appropriate data type."""
        return json.loads(v.strip().lower())

    def read_configuration(filepath):
        """Read metadata and options from setup.cfg located at filepath."""
        cfg = ConfigParser()
        with io.open(filepath, encoding='utf-8') as f:
            cfg.read_file(f)

        md = dict(cfg.items('metadata'))
        for list_key in 'classifiers', 'keywords', 'project_urls':
            try:
                md[list_key] = cfg_val_to_list(md[list_key])
            except KeyError:
                pass
        try:
            md['long_description'] = maybe_read_files(md['long_description'])
        except KeyError:
            pass
        opt = dict(cfg.items('options'))
        for list_key in 'include_package_data', 'use_scm_version', 'zip_safe':
            try:
                opt[list_key] = cfg_val_to_primitive(opt[list_key])
            except KeyError:
                pass
        for list_key in 'scripts', 'install_requires', 'setup_requires':
            try:
                opt[list_key] = cfg_val_to_list(opt[list_key])
            except KeyError:
                pass
        try:
            opt['package_dir'] = cfg_val_to_dict(opt['package_dir'])
        except KeyError:
            pass
        try:
            opt_package_data = dict(cfg.items('options.package_data'))
            if not opt_package_data.get('', '').strip():
                opt_package_data[''] = opt_package_data['*']
                del opt_package_data['*']
        except (KeyError, NoSectionError):
            opt_package_data = {}
        try:
            opt_extras_require = dict(cfg.items('options.extras_require'))
            opt['extras_require'] = {}
            for k, v in opt_extras_require.items():
                opt['extras_require'][k] = cfg_val_to_list(v)
        except NoSectionError:
            pass
        opt['package_data'] = {}
        for k, v in opt_package_data.items():
            opt['package_data'][k] = cfg_val_to_list(v)
        try:
            opt_exclude_package_data = dict(
                cfg.items('options.exclude_package_data'),
            )
            if (
                    not opt_exclude_package_data.get('', '').strip()
                    and '*' in opt_exclude_package_data
            ):
                opt_exclude_package_data[''] = opt_exclude_package_data['*']
                del opt_exclude_package_data['*']
        except NoSectionError:
            pass
        else:
            opt['exclude_package_data'] = {}
            for k, v in opt_exclude_package_data.items():
                opt['exclude_package_data'][k] = cfg_val_to_list(v)
        cur_pkgs = opt.get('packages', '').strip()
        if '\n' in cur_pkgs:
            opt['packages'] = cfg_val_to_list(opt['packages'])
        elif cur_pkgs.startswith('find:'):
            opt_packages_find = stringify_dict_contents(
                dict(cfg.items('options.packages.find'))
            )
            opt['packages'] = setuptools.find_packages(**opt_packages_find)
        return {'metadata': md, 'options': opt}


def cut_local_version_on_upload(version):
    """Generate a PEP440 local version if uploading to PyPI."""
    import os
    import setuptools_scm.version  # only present during setup time
    IS_PYPI_UPLOAD = os.getenv('PYPI_UPLOAD') == 'true'  # set in tox.ini
    return (
        '' if IS_PYPI_UPLOAD
        else setuptools_scm.version.get_local_node_and_date(version)
    )


if HAS_DIST_INFO_CMD:
    class patched_dist_info(setuptools.command.dist_info.dist_info):
        def run(self):
            self.egg_base = str_if_nested_or_str(self.egg_base)
            return setuptools.command.dist_info.dist_info.run(self)


declarative_setup_params = read_configuration('setup.cfg')
"""Declarative metadata and options as read by setuptools."""


setup_params = {}
"""Explicit metadata for passing into setuptools.setup() call."""

setup_params = dict(setup_params, **declarative_setup_params['metadata'])
setup_params = dict(setup_params, **declarative_setup_params['options'])

if HAS_DIST_INFO_CMD:
    setup_params['cmdclass'] = {
        'dist_info': patched_dist_info,
    }

setup_params['use_scm_version'] = {
    'local_scheme': cut_local_version_on_upload,
}

# Patch incorrectly decoded package_dir option
# ``egg_info`` demands native strings failing with unicode under Python 2
# Ref https://github.com/pypa/setuptools/issues/1136
setup_params = stringify_dict_contents(setup_params)


__name__ == '__main__' and setuptools.setup(**setup_params)
