#  Copyright (c) 2015-2018 Cisco Systems, Inc.

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
"""Ansible-Navigator Provisioner Module."""

# pylint: disable=too-many-lines
import logging
import os

import yaml
from ansible_compat.ports import cached_property

from molecule import util
from molecule.provisioner import ansible, ansible_navigator_playbook, ansible_playbooks

LOG = logging.getLogger(__name__)


class MyDumper(yaml.Dumper):
    """Custom YAML dumper to use quotes in output."""

    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


class QuotedString(str):
    """Dummy class to identify quoted string."""


def quoted_scalar(dumper, data):
    """Yaml scaler for quotes."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


class Ansible_Navigator(ansible.Ansible):
    """
    Molecule's provisioner manages the instances lifecycle.  However, the user
    must provide the create, destroy, and converge playbooks.  Molecule's
    ``init`` subcommand will provide the necessary files for convenience.

    Molecule will skip tasks which are tagged with either `molecule-notest` or
    `notest`. With the tag `molecule-idempotence-notest` tasks are only
    skipped during the idempotence action step.

    .. important::

        Reserve the create and destroy playbooks for provisioning.  Do not
        attempt to gather facts or perform operations on the provisioned nodes
        inside these playbooks.  Due to the gymnastics necessary to sync state
        between Ansible and Molecule, it is best to perform these tasks in the
        prepare or converge playbooks.

        It is the developers responsibility to properly map the modules' fact
        data into the instance_conf_dict fact in the create playbook.  This
        allows Molecule to properly configure Ansible inventory.

    Additional options can be passed to ``ansible-playbook`` through the options
    dict.  Any option set in this section will override the defaults.

    .. important::

        Options do not affect the create and destroy actions.

    .. note::

        Molecule will remove any options matching '^[v]+$', and pass ``-vvv``
        to the underlying ``ansible-playbook`` command when executing
        `molecule --debug`.

    Molecule will silence log output, unless invoked with the ``--debug`` flag.
    However, this results in quite a bit of output.  To enable Ansible log
    output, add the following to the ``provisioner`` section of ``molecule.yml``.

    .. code-block:: yaml

        provisioner:
          name: ansible-navigator
          log: True

    The create/destroy playbooks for Docker and Podman are bundled with
    Molecule.  These playbooks have a clean API from `molecule.yml`, and
    are the most commonly used.  The bundled playbooks can still be overridden.

    The playbook loading order is:

    1. provisioner.playbooks.$driver_name.$action
    2. provisioner.playbooks.$action
    3. bundled_playbook.$driver_name.$action

    .. code-block:: yaml

        provisioner:
          name: ansible-navigator
          options:
            vvv: True
          playbooks:
            create: create.yml
            converge: converge.yml
            destroy: destroy.yml

    Share playbooks between roles.

    .. code-block:: yaml

        provisioner:
          name: ansible-navigator
          playbooks:
            create: ../default/create.yml
            destroy: ../default/destroy.yml
            converge: converge.yml

    Multiple driver playbooks.  In some situations a developer may choose to
    test the same role against different backends.  Molecule will choose driver
    specific create/destroy playbooks, if the determined driver has a key in
    the playbooks section of the provisioner's dict.

    .. important::

        If the determined driver has a key in the playbooks dict, Molecule will
        use this dict to resolve all provisioning playbooks (create/destroy).

    .. code-block:: yaml

        provisioner:
          name: ansible-navigator
          playbooks:
            docker:
              create: create.yml
              destroy: destroy.yml
            create: create.yml
            destroy: destroy.yml
            converge: converge.yml

    .. important::

        Paths in this section are converted to absolute paths, where the
        relative parent is the $scenario_directory.

    The side effect playbook executes actions which produce side effects to the
    instances(s).  Intended to test HA failover scenarios or the like.  It is
    not enabled by default.  Add the following to the provisioner's ``playbooks``
    section to enable.

    .. code-block:: yaml

        provisioner:
          name: ansible-navigator
          playbooks:
            side_effect: side_effect.yml

    .. important::

        This feature should be considered experimental.

    The prepare playbook executes actions which bring the system to a given
    state prior to converge.  It is executed after create, and only once for
    the duration of the instances life.

    This can be used to bring instances into a particular state, prior to
    testing.

    .. code-block:: yaml

        provisioner:
          name: ansible-navigator
          playbooks:
            prepare: prepare.yml

    The cleanup playbook is for cleaning up test infrastructure that may not
    be present on the instance that will be destroyed. The primary use-case
    is for "cleaning up" changes that were made outside of Molecule's test
    environment. For example, remote database connections or user accounts.
    Intended to be used in conjunction with `prepare` to modify external
    resources when required.

    The cleanup step is executed directly before every destroy step. Just like
    the destroy step, it will be run twice. An initial clean before converge
    and then a clean before the last destroy step. This means that the cleanup
    playbook must handle failures to cleanup resources which have not
    been created yet.

    Add the following to the provisioner's `playbooks` section
    to enable.

    .. code-block:: yaml

        provisioner:
          name: ansible-navigator
          playbooks:
            cleanup: cleanup.yml

    .. important::

        This feature should be considered experimental.

    Environment variables.  Molecule does its best to handle common Ansible
    paths.

    Environment variables can be passed to the provisioner.  Variables in this
    section which match the names above will be appended to the above defaults,
    and converted to absolute paths, where the relative parent is the
    $scenario_directory.

    .. important::

        Paths in this section are converted to absolute paths, where the
        relative parent is the $scenario_directory.

    .. code-block:: yaml

        provisioner:
          name: ansible-navigator
          config_options:
            ansible-navigator:
              execution-environment:
                environment-variables:
                  set:
                    FOO: bar

    Modifying ansible-navigator.yml

    .. code-block:: yaml

        provisioner:
          name: ansible-navigator
          config_options:
            ansible-navigator:
              execution-environment:
                image: quay.io/ansible/creator-ee:v0.4.2
                pull:
                  policy: missing

    """  # noqa

    def __init__(self, config):
        """
        Initialize a new ansible-navigator class and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(Ansible_Navigator, self).__init__(config)

    @property
    def default_config_options_navigator(self):
        """
        Provide Default options to construct ansible-navigator.yml and returns a dict.

        :return: dict
        """
        role_prefix = None
        role_name = self._config.project_directory.split("/")[-1]
        with open(self._config.project_directory + "/meta/main.yml", "r") as stream:
            try:
                galaxy_info = yaml.safe_load(stream)["galaxy_info"]
                if "role_name" in galaxy_info:
                    role_name = galaxy_info["role_name"]
                if "namespace" in galaxy_info:
                    role_prefix = galaxy_info["namespace"]
                elif "author" in galaxy_info:
                    role_prefix = galaxy_info["author"]
            except yaml.YAMLError as exc:
                print(exc)
        if role_prefix is not None:
            role_name = role_prefix + "." + role_name
        return {
            "ansible-navigator": {
                "ansible": {
                    "config": {
                        "path": "/home/runner/molecule/ansible.cfg",
                    },
                    "inventory": {
                        "entries": [
                            "/home/runner/molecule/inventory/ansible_inventory.yml"
                        ]
                    },
                },
                "mode": "stdout",
                "playbook-artifact": {
                    "enable": True,
                    "save-as": self._config.scenario.ephemeral_directory
                    + "/artifacts/{playbook_name}-artifact-{time_stamp}.json",
                },
                "execution-environment": {
                    "container-engine": "docker",
                    "enabled": True,
                    "pull": {
                        "policy": "missing",
                    },
                    "environment-variables": {
                        "set": {
                            "ANSIBLE_ROLES_PATH": "/home/runner/molecule/roles:/home/runner/roles/:usr/share/ansible/roles:/etc/ansible/roles:~/.ansible/roles",
                            "ANSIBLE_COLLECTIONS_PATH": "/home/runner/molecule/collections:/home/runner/.ansible/collections:/usr/share/ansible/collections:/etc/ansible/collections",
                            "ANSIBLE_FILTER_PLUGINS": "/home/runner/molecule/plugins/filter:/usr/share/ansible/plugins/filter",
                            "ANSIBLE_FORCE_COLOR": "1",
                            "ANSIBLE_LIBRARY": "/home/runner/molecule/library:/home/runner/.ansible/plugins/modules:/usr/share/ansible/plugins/modules",
                            "MOLECULE_FILE": "/home/runner/molecule/molecule.yml",
                            "MOLECULE_VERIFIER_TEST_DIRECTORY": "/home/runner/roles/"
                            + role_name
                            + "/molecule/"
                            + self._config.scenario.name
                            + "/tests",
                        }
                    },
                    "volume-mounts": [
                        {
                            "src": self._config.project_directory,
                            "dest": "/home/runner/roles/" + role_name,
                        },
                        {
                            "src": self._config.scenario.ephemeral_directory,
                            "dest": "/home/runner/molecule",
                        },
                        {
                            "src": os.getenv("HOME") + "/.docker",
                            "dest": "/home/runner/.docker",
                        },
                        {"src": "/var/run/", "dest": "/tmp/run/"},
                    ],
                    "container-options": [
                        # DOCKER_HOST have to be set here so it dose not override the Host Env
                        QuotedString("--env=DOCKER_HOST=unix:///runner/docker.sock")
                    ],
                },
            },
        }

    @property
    def config_options(self):
        return util.merge_dicts(
            self.default_config_options,
            self._config.config["provisioner"]["config_options"].get("ansible", {}),
        )

    @property
    def config_options_navigator(self):
        config_molecule = self._config.config["provisioner"]["config_options"].copy()
        config_molecule.pop("ansible", None)
        return util.merge_dicts(
            self.default_config_options_navigator,
            config_molecule,
        )

    @property
    def name(self):
        return self._config.config["provisioner"]["name"]

    @property
    def options(self):
        if self._config.action in ["create", "destroy"]:
            return self.default_options

        o = self._config.config["provisioner"]["options"]
        # NOTE(retr0h): Remove verbose options added by the user while in
        # debug.
        if self._config.debug:
            o = util.filter_verbose_permutation(o)

        return util.merge_dicts(self.default_options, o)

    @property
    def env(self):
        default_env = super().env
        env = self._config.config["provisioner"]["env"].copy()
        # ensure that all keys and values are strings
        env = {str(k): str(v) for k, v in env.items()}
        env["ANSIBLE_NAVIGATOR_CONFIG"] = os.path.join(
            self._config.scenario.ephemeral_directory, "ansible-navigator.yml"
        )

        return util.merge_dicts(default_env, env)

    @property
    def config_file_navigator(self):
        return os.path.join(
            self._config.scenario.ephemeral_directory, "ansible-navigator.yml"
        )

    @cached_property
    def playbooks(self):
        return ansible_playbooks.AnsiblePlaybooks(self._config)

    def cleanup(self):
        """
        Execute `ansible-playbook` against the cleanup playbook and returns \
        None.

        :return: None
        """
        pb = self._get_ansible_playbook(self.playbooks.cleanup)
        pb.execute()

    def connection_options(self, instance_name):
        d = self._config.driver.ansible_connection_options(instance_name)

        return util.merge_dicts(
            d, self._config.config["provisioner"]["connection_options"]
        )

    def check(self):
        """
        Execute ``ansible-playbook`` against the converge playbook with the \
        ``--check`` flag and returns None.

        :return: None
        """
        pb = self._get_ansible_playbook(self.playbooks.converge)
        pb.add_cli_arg("check", True)
        pb.execute()

    def converge(self, playbook=None, **kwargs):
        """
        Execute ``ansible-playbook`` against the converge playbook unless \
        specified otherwise and returns a string.

        :param playbook: An optional string containing an absolute path to a
         playbook.
        :param kwargs: An optional keyword arguments.
        :return: str
        """
        pb = self._get_ansible_playbook(playbook or self.playbooks.converge, **kwargs)

        return pb.execute()

    def destroy(self):
        """
        Execute ``ansible-playbook`` against the destroy playbook and returns \
        None.

        :return: None
        """
        pb = self._get_ansible_playbook(self.playbooks.destroy)
        pb.execute()

    def side_effect(self, action_args=None):
        """
        Execute ``ansible-playbook`` against the side_effect playbook and \
        returns None.

        :return: None
        """
        if action_args:
            playbooks = [
                self._get_ansible_playbook(self._config.provisioner.abs_path(playbook))
                for playbook in action_args
            ]
        else:
            playbooks = [self._get_ansible_playbook(self.playbooks.side_effect)]
        for pb in playbooks:
            pb.execute()

    def create(self):
        """
        Execute ``ansible-playbook`` against the create playbook and returns \
        None.

        :return: None
        """
        pb = self._get_ansible_playbook(self.playbooks.create)
        pb.execute()

    def prepare(self):
        """
        Execute ``ansible-playbook`` against the prepare playbook and returns \
        None.

        :return: None
        """
        pb = self._get_ansible_playbook(self.playbooks.prepare)
        pb.execute()

    def syntax(self):
        """
        Execute ``ansible-playbook`` against the converge playbook with the \
        ``-syntax-check`` flag and returns None.

        :return: None
        """
        pb = self._get_ansible_playbook(self.playbooks.converge)
        pb.add_cli_arg("syntax-check", True)
        pb.execute()

    def verify(self, action_args=None):
        """
        Execute ``ansible-playbook`` against the verify playbook and returns \
        None.

        :return: None
        """
        if action_args:
            playbooks = [
                self._config.provisioner.abs_path(playbook) for playbook in action_args
            ]
        else:
            playbooks = [self.playbooks.verify]
        if not playbooks:
            LOG.warning("Skipping, verify playbook not configured.")
            return
        for playbook in playbooks:
            # Get ansible playbooks for `verify` instead of `provision`
            pb = self._get_ansible_playbook(playbook, verify=True)
            pb.execute()

    def write_config(self):
        MyDumper.add_representer(QuotedString, quoted_scalar)
        util.write_file(
            self.config_file_navigator,
            yaml.dump(self.config_options_navigator, Dumper=MyDumper),
        )
        super().write_config()

    def _get_ansible_playbook(self, playbook, verify=False, **kwargs):
        """
        Get an instance of AnsiblePlaybook and returns it.

        :param playbook: A string containing an absolute path to a
         provisioner's playbook.
        :param verify: An optional bool to toggle the Plabook mode between
         provision and verify. False: provision; True: verify. Default is False.
        :param kwargs: An optional keyword arguments.
        :return: object
        """
        return ansible_navigator_playbook.AnsiblePlaybook(
            playbook, self._config, verify, **kwargs
        )
