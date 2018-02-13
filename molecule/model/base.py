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

import marshmallow

from molecule import logger

LOG = logger.get_logger(__name__)


class BaseUnknown(marshmallow.Schema):
    @marshmallow.validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        unknown = set(original_data) - set(self.fields)
        if unknown:
            raise marshmallow.ValidationError('Unknown field', unknown)


class BaseDisallowed(marshmallow.Schema):
    @marshmallow.validates_schema()
    def check_fields(self, data):
        defaults = data.get('defaults')
        if defaults:
            disallowed_list = ['roles_path', 'library', 'filter_plugins']
            if any(disallowed in defaults for disallowed in disallowed_list):
                raise marshmallow.ValidationError(
                    'Disallowed user provided config option', defaults)

        privilege_escalation = data.get('privilege_escalation')
        if privilege_escalation:
            raise marshmallow.ValidationError(
                'Disallowed user provided config option',
                'privilege_escalation')
