# Copyright 2015 Docker, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# Taken from Docker Compose:
# https://github.com/docker/compose/blob/master/compose/config/interpolation.py

import string


class InvalidInterpolation(Exception):
    def __init__(self, string, place):
        self.string = string
        self.place = place


class Interpolator(object):
    """
    Configuration options may contain environment variables.  For example,
    suppose the shell contains `VERIFIER_NAME=testinfra` and the following
    molecule.yml is supplied.

    .. code-block:: yaml

        verifier:
          - name: ${VERIFIER_NAME}

    Molecule will substitute `$VERIFIER_NAME` with the value of the
    `VERIFIER_NAME` environment variable.

    .. warning::

        If an environment variable is not set, Molecule substitutes with an
        empty string.

    Both `$VARIABLE` and `${VARIABLE}` syntax are supported. Extended
    shell-style features, such as `${VARIABLE-default}` and
    `${VARIABLE:-default}` are also supported.

    If a literal dollar sign is needed in a configuration, use a double dollar
    sign (`$$`).
    """

    def __init__(self, templater, mapping):
        self.templater = templater
        self.mapping = mapping

    def interpolate(self, string):
        try:
            return self.templater(string).substitute(self.mapping)
        except ValueError as e:
            raise InvalidInterpolation(string, e)


class TemplateWithDefaults(string.Template):
    idpattern = r'[_a-z][_a-z0-9]*(?::?-[^}]+)?'

    # Modified from python2.7/string.py
    def substitute(self, mapping):
        # Helper function for .sub()
        def convert(mo):
            # Check the most common path first.
            named = mo.group('named') or mo.group('braced')
            if named is not None:
                if ':-' in named:
                    var, _, default = named.partition(':-')
                    return mapping.get(var) or default
                if '-' in named:
                    var, _, default = named.partition('-')
                    return mapping.get(var, default)
                val = mapping.get(named, '')
                return '%s' % (val, )
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                self._invalid(mo)

        return self.pattern.sub(convert, self.template)
