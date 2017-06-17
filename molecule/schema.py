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


class SchemaBase(marshmallow.Schema):
    @marshmallow.validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        unknown = set(original_data) - set(self.fields)
        if unknown:
            raise marshmallow.ValidationError('Unknown field', unknown)


class DependencySchema(SchemaBase):
    name = marshmallow.fields.Str()
    enabled = marshmallow.fields.Bool()
    options = marshmallow.fields.Dict()
    env = marshmallow.fields.Dict()


class DriverSchema(SchemaBase):
    name = marshmallow.fields.Str()
    options = marshmallow.fields.Dict()
    ssh_connection_options = marshmallow.fields.List(marshmallow.fields.Str)
    safe_files = marshmallow.fields.List(marshmallow.fields.Str)


class LintSchema(SchemaBase):
    name = marshmallow.fields.Str()
    enabled = marshmallow.fields.Bool()
    options = marshmallow.fields.Dict()
    env = marshmallow.fields.Dict()
    trailing_ignore_paths = marshmallow.fields.List(marshmallow.fields.Str)


class PlatformsSchema(marshmallow.Schema):
    name = marshmallow.fields.Str()


class ProvisionerInventoryLinksSchema(SchemaBase):
    host_vars = marshmallow.fields.Str()
    group_vars = marshmallow.fields.Str()


class ProvisionerInventorySchema(SchemaBase):
    host_vars = marshmallow.fields.Dict()
    group_vars = marshmallow.fields.Dict()
    links = marshmallow.fields.Nested(ProvisionerInventoryLinksSchema())


class ProvisionerPlaybooksSchema(SchemaBase):
    setup = marshmallow.fields.Str()
    converge = marshmallow.fields.Str()
    teardown = marshmallow.fields.Str()


class ProvisionerSchema(SchemaBase):
    name = marshmallow.fields.Str()
    config_options = marshmallow.fields.Dict()
    connection_options = marshmallow.fields.Dict()
    options = marshmallow.fields.Dict()
    env = marshmallow.fields.Dict()
    inventory = marshmallow.fields.Nested(ProvisionerInventorySchema())
    children = marshmallow.fields.Dict()
    playbooks = marshmallow.fields.Nested(ProvisionerPlaybooksSchema())


class ScenarioSchema(SchemaBase):
    name = marshmallow.fields.Str()
    check_sequence = marshmallow.fields.List(marshmallow.fields.Str)
    converge_sequence = marshmallow.fields.List(marshmallow.fields.Str)
    test_sequence = marshmallow.fields.List(marshmallow.fields.Str)


class VerifierSchema(SchemaBase):
    name = marshmallow.fields.Str()
    enabled = marshmallow.fields.Bool()
    directory = marshmallow.fields.Str()
    options = marshmallow.fields.Dict()
    env = marshmallow.fields.Dict()


class MoleculeSchema(marshmallow.Schema):
    dependency = marshmallow.fields.Nested(DependencySchema())
    driver = marshmallow.fields.Nested(DriverSchema())
    lint = marshmallow.fields.Nested(LintSchema())
    platforms = marshmallow.fields.List(
        marshmallow.fields.Nested(PlatformsSchema(), only='name'))
    provisioner = marshmallow.fields.Nested(ProvisionerSchema())
    scenario = marshmallow.fields.Nested(ScenarioSchema())
    verifier = marshmallow.fields.Nested(VerifierSchema())


def validate(c):
    schema = MoleculeSchema(strict=True)

    return schema.load(c)
