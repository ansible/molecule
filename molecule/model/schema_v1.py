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
from molecule.model import base

LOG = logger.get_logger(__name__)


class AnsibleSchema(base.BaseUnknown):
    config_file = marshmallow.fields.Str()
    playbook = marshmallow.fields.Str()
    raw_env_vars = marshmallow.fields.Dict()
    extra_vars = marshmallow.fields.Str()
    verbose = marshmallow.fields.Bool()
    become = marshmallow.fields.Bool()
    tags = marshmallow.fields.Str()


class DriverSchema(base.BaseUnknown):
    name = marshmallow.fields.Str()


class PlatformSchema(base.BaseUnknown):
    name = marshmallow.fields.Str()
    box = marshmallow.fields.Str()
    box_version = marshmallow.fields.Str()
    box_url = marshmallow.fields.Str()


class ProviderOptionsSchema(base.BaseUnknown):
    memory = marshmallow.fields.Int()
    cpus = marshmallow.fields.Int()


class ProviderSchema(base.BaseUnknown):
    name = marshmallow.fields.Str()
    type = marshmallow.fields.Str()
    options = marshmallow.fields.Nested(ProviderOptionsSchema())


class InterfaceSchema(base.BaseUnknown):
    network_name = marshmallow.fields.Str()
    type = marshmallow.fields.Str()
    auto_config = marshmallow.fields.Bool()
    ip = marshmallow.fields.Str()


class InstanceOptionsSchema(base.BaseUnknown):
    append_platform_to_hostname = marshmallow.fields.Bool()


class InstanceSchema(base.BaseUnknown):
    name = marshmallow.fields.Str()
    ansible_groups = marshmallow.fields.List(marshmallow.fields.Str())
    interfaces = marshmallow.fields.List(
        marshmallow.fields.Nested(InterfaceSchema()))
    raw_config_args = marshmallow.fields.List(marshmallow.fields.Str())
    options = marshmallow.fields.Nested(InstanceOptionsSchema())


class VagrantSchema(base.BaseUnknown):
    platforms = marshmallow.fields.List(
        marshmallow.fields.Nested(PlatformSchema()))
    providers = marshmallow.fields.List(
        marshmallow.fields.Nested(ProviderSchema()))
    instances = marshmallow.fields.List(
        marshmallow.fields.Nested(InstanceSchema()))


class VerifierOptionsSchema(base.BaseUnknown):
    sudo = marshmallow.fields.Bool()


class VerifierSchema(base.BaseUnknown):
    name = marshmallow.fields.Str()
    options = marshmallow.fields.Nested(VerifierOptionsSchema())


class MoleculeSchema(marshmallow.Schema):
    ansible = marshmallow.fields.Nested(AnsibleSchema())
    vagrant = marshmallow.fields.Nested(VagrantSchema())
    driver = marshmallow.fields.Nested(DriverSchema())
    verifier = marshmallow.fields.Nested(VerifierSchema())


def validate(c):
    schema = MoleculeSchema(strict=True)

    return schema.load(c)
