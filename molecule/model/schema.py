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


class DependencySchema(base.BaseUnknown):
    name = marshmallow.fields.Str()
    enabled = marshmallow.fields.Bool()
    options = marshmallow.fields.Dict()
    env = marshmallow.fields.Dict()


class DriverProviderSchema(base.BaseUnknown):
    name = marshmallow.fields.Str(allow_none=True)


class DriverSchema(base.BaseUnknown):
    name = marshmallow.fields.Str()
    provider = marshmallow.fields.Nested(DriverProviderSchema())
    options = marshmallow.fields.Dict()
    ssh_connection_options = marshmallow.fields.List(marshmallow.fields.Str())
    safe_files = marshmallow.fields.List(marshmallow.fields.Str())


class LintSchema(base.BaseUnknown):
    name = marshmallow.fields.Str()
    enabled = marshmallow.fields.Bool()
    options = marshmallow.fields.Dict()
    env = marshmallow.fields.Dict()


class InterfaceSchema(base.BaseUnknown):
    network_name = marshmallow.fields.Str()
    type = marshmallow.fields.Str()
    auto_config = marshmallow.fields.Bool()
    ip = marshmallow.fields.Str()


class PlatformsBaseSchema(marshmallow.Schema):
    name = marshmallow.fields.Str()
    groups = marshmallow.fields.List(marshmallow.fields.Str())
    children = marshmallow.fields.List(marshmallow.fields.Str())
    state = marshmallow.fields.List(marshmallow.fields.Str())
    append_scenario = marshmallow.fields.Bool()


class PlatformsSchema(PlatformsBaseSchema):
    pass


class PlatformsDockerNetworksSchema(marshmallow.Schema):
    name = marshmallow.fields.Str()


class PlatformsDockerSchema(marshmallow.Schema):
    hostname = marshmallow.fields.Str()
    image = marshmallow.fields.Str()
    recreate = marshmallow.fields.Bool()
    log_driver = marshmallow.fields.Str()
    command = marshmallow.fields.Str()
    privileged = marshmallow.fields.Bool()
    volumes = marshmallow.fields.List(marshmallow.fields.Str())
    capabilities = marshmallow.fields.List(marshmallow.fields.Str())
    ulimits = marshmallow.fields.List(marshmallow.fields.Str())
    networks = marshmallow.fields.List(
        marshmallow.fields.Nested(PlatformsDockerNetworksSchema))
    dns_servers = marshmallow.fields.List(marshmallow.fields.Str())


class PlatformsVagrantSchema(PlatformsBaseSchema):
    box = marshmallow.fields.Str()
    box_version = marshmallow.fields.Str()
    box_url = marshmallow.fields.Str()
    memory = marshmallow.fields.Int()
    cpus = marshmallow.fields.Int()
    raw_config_args = marshmallow.fields.List(marshmallow.fields.Str())
    interfaces = marshmallow.fields.List(
        marshmallow.fields.Nested(InterfaceSchema()))
    provider = marshmallow.fields.Str()
    force_stop = marshmallow.fields.Bool()


class ProvisionerInventoryLinksSchema(base.BaseUnknown):
    host_vars = marshmallow.fields.Str()
    group_vars = marshmallow.fields.Str()


class ProvisionerInventorySchema(base.BaseUnknown):
    host_vars = marshmallow.fields.Dict()
    group_vars = marshmallow.fields.Dict()
    links = marshmallow.fields.Nested(ProvisionerInventoryLinksSchema())


class PlaybooksSchema(base.BaseUnknown):
    create = marshmallow.fields.Str()
    converge = marshmallow.fields.Str()
    destroy = marshmallow.fields.Str()
    prepare = marshmallow.fields.Str()
    side_effect = marshmallow.fields.Str(allow_none=True)


class ProvisionerPlaybooksSchema(PlaybooksSchema):
    docker = marshmallow.fields.Nested(PlaybooksSchema())
    ec2 = marshmallow.fields.Nested(PlaybooksSchema())
    gce = marshmallow.fields.Nested(PlaybooksSchema())
    lxc = marshmallow.fields.Nested(PlaybooksSchema())
    lxd = marshmallow.fields.Nested(PlaybooksSchema())
    openstack = marshmallow.fields.Nested(PlaybooksSchema())
    vagrant = marshmallow.fields.Nested(PlaybooksSchema())


class ProvisionerConfigOptionsSchema(base.BaseDisallowed):
    defaults = marshmallow.fields.Dict()
    privilege_escalation = marshmallow.fields.Dict()


class ProvisionerSchema(base.BaseUnknown):
    name = marshmallow.fields.Str()
    config_options = marshmallow.fields.Nested(
        ProvisionerConfigOptionsSchema())
    connection_options = marshmallow.fields.Dict()
    options = marshmallow.fields.Dict()
    env = marshmallow.fields.Dict()
    inventory = marshmallow.fields.Nested(ProvisionerInventorySchema())
    children = marshmallow.fields.Dict()
    playbooks = marshmallow.fields.Nested(ProvisionerPlaybooksSchema())
    lint = marshmallow.fields.Nested(LintSchema())


class ScenarioSchema(base.BaseUnknown):
    name = marshmallow.fields.Str()
    check_sequence = marshmallow.fields.List(marshmallow.fields.Str())
    converge_sequence = marshmallow.fields.List(marshmallow.fields.Str())
    create_sequence = marshmallow.fields.List(marshmallow.fields.Str())
    destroy_sequence = marshmallow.fields.List(marshmallow.fields.Str())
    test_sequence = marshmallow.fields.List(marshmallow.fields.Str())


class VerifierSchema(base.BaseUnknown):
    name = marshmallow.fields.Str()
    enabled = marshmallow.fields.Bool()
    directory = marshmallow.fields.Str()
    options = marshmallow.fields.Dict()
    env = marshmallow.fields.Dict()
    additional_files_or_dirs = marshmallow.fields.List(
        marshmallow.fields.Str())
    lint = marshmallow.fields.Nested(LintSchema())


class MoleculeBaseSchema(base.BaseUnknown):
    dependency = marshmallow.fields.Nested(DependencySchema())
    driver = marshmallow.fields.Nested(DriverSchema())
    lint = marshmallow.fields.Nested(LintSchema())
    provisioner = marshmallow.fields.Nested(ProvisionerSchema())
    scenario = marshmallow.fields.Nested(ScenarioSchema())
    verifier = marshmallow.fields.Nested(VerifierSchema())


class MoleculeDockerSchema(MoleculeBaseSchema):
    platforms = marshmallow.fields.List(
        marshmallow.fields.Nested(PlatformsDockerSchema()))


class MoleculeVagrantSchema(MoleculeBaseSchema):
    platforms = marshmallow.fields.List(
        marshmallow.fields.Nested(PlatformsVagrantSchema()))


class MoleculeSchema(MoleculeBaseSchema):
    platforms = marshmallow.fields.List(
        marshmallow.fields.Nested(PlatformsSchema()))


def validate(c):
    if c['driver']['name'] == 'vagrant':
        schema = MoleculeVagrantSchema(strict=True)
    elif c['driver']['name'] == 'docker':
        schema = MoleculeDockerSchema(strict=True)
    else:
        schema = MoleculeSchema(strict=True)

    return schema.load(c)
