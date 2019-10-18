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


def cut_local_version_on_upload(version):
    """Generate a PEP440 local version if uploading to PyPI."""
    import os
    import setuptools_scm.version  # only present during setup time

    IS_PYPI_UPLOAD = os.getenv('PYPI_UPLOAD') == 'true'  # set in tox.ini
    return (
        ''
        if IS_PYPI_UPLOAD
        else setuptools_scm.version.get_local_node_and_date(version)
    )


setup_params = {}
setup_params['use_scm_version'] = {'local_scheme': cut_local_version_on_upload}


__name__ == '__main__' and setuptools.setup(**setup_params)
