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
"""Ansible Provisioner Module."""

# pylint: disable=too-many-lines
import collections
import copy
import logging
import os
import shutil
from typing import List, Optional

from ansible_compat.ports import cached_property

from molecule import util
from molecule.api import drivers
from molecule.provisioner import ansible_playbook, ansible_playbooks, base

LOG = logging.getLogger(__name__)


class Ansible(base.Base):
    """
    `Ansible`_ is the default provisioner.  No other provisioner will be \
    supported.

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
          name: ansible
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
          name: ansible
          options:
            vvv: True
          playbooks:
            create: create.yml
            converge: converge.yml
            destroy: destroy.yml

    Share playbooks between roles.

    .. code-block:: yaml

        provisioner:
          name: ansible
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
          name: ansible
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
          name: ansible
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
          name: ansible
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
          name: ansible
          playbooks:
            cleanup: cleanup.yml

    .. important::

        This feature should be considered experimental.

    Environment variables.  Molecule does its best to handle common Ansible
    paths.  The defaults are as follows.

    ::

        ANSIBLE_ROLES_PATH:
          $runtime_cache_dir/roles:$ephemeral_directory/roles/:$project_directory/../:~/.ansible/roles:/usr/share/ansible/roles:/etc/ansible/roles
        ANSIBLE_LIBRARY:
          $ephemeral_directory/modules/:$project_directory/library/:~/.ansible/plugins/modules:/usr/share/ansible/plugins/modules
        ANSIBLE_FILTER_PLUGINS:
          $ephemeral_directory/plugins/filter/:$project_directory/filter/plugins/:~/.ansible/plugins/filter:/usr/share/ansible/plugins/modules

    Environment variables can be passed to the provisioner.  Variables in this
    section which match the names above will be appended to the above defaults,
    and converted to absolute paths, where the relative parent is the
    $scenario_directory.

    .. important::

        Paths in this section are converted to absolute paths, where the
        relative parent is the $scenario_directory.

    .. code-block:: yaml

        provisioner:
          name: ansible
          env:
            FOO: bar

    Modifying ansible.cfg.

    .. code-block:: yaml

        provisioner:
          name: ansible
          config_options:
            defaults:
              fact_caching: jsonfile
            ssh_connection:
              scp_if_ssh: True

    .. important::

        The following keys are disallowed to prevent Molecule from
        improperly functioning.  They can be specified through the
        provisioner's env setting described above, with the exception
        of the `privilege_escalation`.

    .. code-block:: yaml

        provisioner:
          name: ansible
          config_options:
            defaults:
              roles_path: /path/to/roles_path
              library: /path/to/library
              filter_plugins: /path/to/filter_plugins
            privilege_escalation: {}

    Roles which require host/groups to have certain variables set.  Molecule
    uses the same `variables defined in a playbook`_ syntax as `Ansible`_.

    .. code-block:: yaml

        provisioner:
          name: ansible
          inventory:
            group_vars:
              foo1:
                foo: bar
              foo2:
                foo: bar
                baz:
                  qux: zzyzx
            host_vars:
              foo1-01:
                foo: bar

    Molecule automatically generates the inventory based on the hosts defined
    under `Platforms`_. Using the ``hosts`` key allows to add extra hosts to
    the inventory that are not managed by Molecule.

    A typical use case is if you want to access some variables from another
    host in the inventory (using hostvars) without creating it.

    .. note::

        The content of ``hosts`` should follow the YAML based inventory syntax:
        start with the ``all`` group and have hosts/vars/children entries.

    .. code-block:: yaml

        provisioner:
          name: ansible
          inventory:
            hosts:
              all:
                hosts:
                  extra_host:
                    foo: hello

    .. important::

        The extra hosts added to the inventory using this key won't be
        created/destroyed by Molecule. It is the developers responsibility
        to target the proper hosts in the playbook. Only the hosts defined
        under `Platforms`_ should be targeted instead of ``all``.


    An alternative to the above is symlinking.  Molecule creates symlinks to
    the specified directory in the inventory directory. This allows ansible to
    converge utilizing its built in host/group_vars resolution. These two
    forms of inventory management are mutually exclusive.

    Like above, it is possible to pass an additional inventory file
    (or even dynamic inventory script), using the ``hosts`` key. `Ansible`_ will
    automatically merge this inventory with the one generated by molecule.
    This can be useful if you want to define extra hosts that are not managed
    by Molecule.

    .. important::

        Again, it is the developers responsibility to target the proper hosts
        in the playbook. Only the hosts defined under
        `Platforms`_ should be targeted instead of ``all``.

    .. note::

        The source directory linking is relative to the scenario's
        directory.

        The only valid keys are ``hosts``, ``group_vars`` and ``host_vars``.  Molecule's
        schema validator will enforce this.


    .. code-block:: yaml

        provisioner:
          name: ansible
          inventory:
            links:
              hosts: ../../../inventory/hosts
              group_vars: ../../../inventory/group_vars/
              host_vars: ../../../inventory/host_vars/

    .. important::

        You can use either `hosts`/`group_vars`/`host_vars` sections of inventory OR `links`.
        If you use both, links will win.

    .. code-block:: yaml

        provisioner:
          name: ansible
          hosts:
            all:
              hosts:
                ignored:
                   important: this host is ignored
          inventory:
            links:
              hosts: ../../../inventory/hosts


    Override connection options:

    .. code-block:: yaml

        provisioner:
          name: ansible
          connection_options:
            ansible_ssh_user: foo
            ansible_ssh_common_args: -o IdentitiesOnly=no

    .. _`variables defined in a playbook`: https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#defining-variables-in-a-playbook

    Add arguments to ansible-playbook when running converge:

    .. code-block:: yaml

        provisioner:
          name: ansible
          ansible_args:
            - --inventory=mygroups.yml
            - --limit=host1,host2

    """  # noqa

    def __init__(self, config):
        """
        Initialize a new ansible class and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(Ansible, self).__init__(config)

    @property
    def default_config_options(self):
        """
        Provide Default options to construct ansible.cfg and returns a dict.

        :return: dict
        """
        return {
            "defaults": {
                "ansible_managed": "Ansible managed: Do NOT edit this file manually!",
                "display_failed_stderr": True,
                "forks": 50,
                "retry_files_enabled": False,
                "host_key_checking": False,
                "nocows": 1,
                "interpreter_python": "auto_silent",
            },
            "ssh_connection": {
                "scp_if_ssh": True,
                "control_path": "%(directory)s/%%h-%%p-%%r",
            },
        }

    @property
    def default_options(self):
        d = {"skip-tags": "molecule-notest,notest"}

        if self._config.action == "idempotence":
            d["skip-tags"] += ",molecule-idempotence-notest"

        if self._config.debug:
            d["vvv"] = True
            d["diff"] = True

        return d

    @property
    def default_env(self):
        # Finds if the current project is part of an ansible_collections hierarchy
        collection_indicator = "ansible_collections"
        # isolating test environment by injects ephemeral scenario directory on
        # top of the collection_path_list. This prevents dependency commands
        # from installing dependencies to user list of collections.
        collections_path_list = [
            util.abs_path(
                os.path.join(
                    self._config.scenario.config.runtime.cache_dir, "collections"
                )
            ),
            util.abs_path(
                os.path.join(self._config.scenario.ephemeral_directory, "collections")
            ),
        ]
        if collection_indicator in self._config.project_directory:
            collection_path, right = self._config.project_directory.rsplit(
                collection_indicator, 1
            )
            collections_path_list.append(util.abs_path(collection_path))
        collections_path_list.extend(
            [
                util.abs_path(
                    os.path.join(os.path.expanduser("~"), ".ansible/collections")
                ),
                "/usr/share/ansible/collections",
                "/etc/ansible/collections",
            ]
        )

        roles_path_list = [
            util.abs_path(
                os.path.join(self._config.scenario.config.runtime.cache_dir, "roles")
            ),
            util.abs_path(
                os.path.join(self._config.scenario.ephemeral_directory, "roles")
            ),
            util.abs_path(os.path.join(self._config.project_directory, os.path.pardir)),
            util.abs_path(os.path.join(os.path.expanduser("~"), ".ansible", "roles")),
            "/usr/share/ansible/roles",
            "/etc/ansible/roles",
        ]

        if os.environ.get("ANSIBLE_ROLES_PATH", ""):
            roles_path_list.extend(
                list(map(util.abs_path, os.environ["ANSIBLE_ROLES_PATH"].split(":")))
            )

        env = util.merge_dicts(
            os.environ,
            {
                "ANSIBLE_CONFIG": self._config.provisioner.config_file,
                "ANSIBLE_ROLES_PATH": ":".join(roles_path_list),
                self._config.ansible_collections_path: ":".join(collections_path_list),
                "ANSIBLE_LIBRARY": ":".join(self._get_modules_directories()),
                "ANSIBLE_FILTER_PLUGINS": ":".join(
                    [
                        self._get_filter_plugin_directory(),
                        util.abs_path(
                            os.path.join(
                                self._config.scenario.ephemeral_directory,
                                "plugins",
                                "filter",
                            )
                        ),
                        util.abs_path(
                            os.path.join(
                                self._config.project_directory, "plugins", "filter"
                            )
                        ),
                        util.abs_path(
                            os.path.join(
                                os.path.expanduser("~"), ".ansible", "plugins", "filter"
                            )
                        ),
                        "/usr/share/ansible/plugins/filter",
                    ]
                ),
            },
        )
        env = util.merge_dicts(env, self._config.env)

        return env

    @property
    def name(self):
        return self._config.config["provisioner"]["name"]

    @property
    def ansible_args(self):
        return self._config.config["provisioner"]["ansible_args"]

    @property
    def config_options(self):
        return util.merge_dicts(
            self.default_config_options,
            self._config.config["provisioner"]["config_options"],
        )

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
        default_env = self.default_env
        env = self._config.config["provisioner"]["env"].copy()
        # ensure that all keys and values are strings
        env = {str(k): str(v) for k, v in env.items()}

        roles_path = default_env["ANSIBLE_ROLES_PATH"]
        library_path = default_env["ANSIBLE_LIBRARY"]
        filter_plugins_path = default_env["ANSIBLE_FILTER_PLUGINS"]

        try:
            path = self._absolute_path_for(env, "ANSIBLE_ROLES_PATH")
            roles_path = f"{roles_path}:{path}"
        except KeyError:
            pass

        try:
            path = self._absolute_path_for(env, "ANSIBLE_LIBRARY")
            library_path = f"{library_path}:{path}"
        except KeyError:
            pass

        try:
            path = self._absolute_path_for(env, "ANSIBLE_FILTER_PLUGINS")
            filter_plugins_path = f"{filter_plugins_path}:{path}"
        except KeyError:
            pass

        env["ANSIBLE_ROLES_PATH"] = roles_path
        env["ANSIBLE_LIBRARY"] = library_path
        env["ANSIBLE_FILTER_PLUGINS"] = filter_plugins_path

        return util.merge_dicts(default_env, env)

    @property
    def hosts(self):
        return self._config.config["provisioner"]["inventory"]["hosts"]

    @property
    def host_vars(self):
        return self._config.config["provisioner"]["inventory"]["host_vars"]

    @property
    def group_vars(self):
        return self._config.config["provisioner"]["inventory"]["group_vars"]

    @property
    def links(self):
        return self._config.config["provisioner"]["inventory"]["links"]

    @property
    def inventory(self):
        """
        Create an inventory structure and returns a dict.

        .. code-block:: yaml
            ungrouped:
              vars:
                foo: bar
              hosts:
                instance-1:
                instance-2:
              children:
                $child_group_name:
                  hosts:
                    instance-1:
                    instance-2:
            $group_name:
              hosts:
                instance-1:
                  ansible_connection: docker
                instance-2:
                  ansible_connection: docker

        :return: str
        """
        dd = self._vivify()
        for platform in self._config.platforms.instances:
            for group in platform.get("groups", ["ungrouped"]):
                instance_name = platform["name"]
                connection_options = self.connection_options(instance_name)
                molecule_vars = {
                    "molecule_file": "{{ lookup('env', 'MOLECULE_FILE') }}",
                    "molecule_ephemeral_directory": "{{ lookup('env', 'MOLECULE_EPHEMERAL_DIRECTORY') }}",
                    "molecule_scenario_directory": "{{ lookup('env', 'MOLECULE_SCENARIO_DIRECTORY') }}",
                    "molecule_yml": "{{ lookup('file', molecule_file) | from_yaml }}",
                    "molecule_instance_config": "{{ lookup('env', 'MOLECULE_INSTANCE_CONFIG') }}",
                    "molecule_no_log": "{{ lookup('env', 'MOLECULE_NO_LOG') or not "
                    "molecule_yml.provisioner.log|default(False) | bool }}",
                }

                # All group
                dd["all"]["hosts"][instance_name] = connection_options
                dd["all"]["vars"] = molecule_vars
                # Named group
                dd[group]["hosts"][instance_name] = connection_options
                dd[group]["vars"] = molecule_vars
                # Ungrouped
                dd["ungrouped"]["vars"] = {}
                # Children
                for child_group in platform.get("children", []):
                    dd[group]["children"][child_group]["hosts"][
                        instance_name
                    ] = connection_options

        return self._default_to_regular(dd)

    @property
    def inventory_directory(self):
        return self._config.scenario.inventory_directory

    @property
    def inventory_file(self):
        return os.path.join(self.inventory_directory, "ansible_inventory.yml")

    @property
    def config_file(self):
        return os.path.join(self._config.scenario.ephemeral_directory, "ansible.cfg")

    @cached_property
    def playbooks(self):
        return ansible_playbooks.AnsiblePlaybooks(self._config)

    @property
    def directory(self):
        return os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            os.path.pardir,
            "molecule",
            "provisioner",
            "ansible",
        )

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
        """
        Write the provisioner's config file to disk and returns None.

        :return: None
        """
        template = util.render_template(
            self._get_config_template(), config_options=self.config_options
        )
        util.write_file(self.config_file, template)

    def manage_inventory(self):
        """
        Manage inventory for Ansible and returns None.

        :returns: None
        """
        self._write_inventory()
        self._remove_vars()
        if not self.links:
            self._add_or_update_vars()
        else:
            self._link_or_update_vars()

    def abs_path(self, path: str) -> Optional[str]:
        return util.abs_path(os.path.join(self._config.scenario.directory, path))

    def _add_or_update_vars(self):
        """
        Create host and/or group vars and returns None.

        :returns: None
        """
        # Create the hosts extra inventory source (only if not empty)
        hosts_file = os.path.join(self.inventory_directory, "hosts")
        if self.hosts:
            util.write_file(hosts_file, util.safe_dump(self.hosts))
        # Create the host_vars and group_vars directories
        for target in ["host_vars", "group_vars"]:
            if target == "host_vars":
                vars_target = copy.deepcopy(self.host_vars)
                for instance_name, _ in self.host_vars.items():
                    instance_key = instance_name
                    vars_target[instance_key] = vars_target.pop(instance_name)

            elif target == "group_vars":
                vars_target = self.group_vars

            if vars_target:
                target_vars_directory = os.path.join(self.inventory_directory, target)

                if not os.path.isdir(util.abs_path(target_vars_directory)):
                    os.mkdir(util.abs_path(target_vars_directory))

                for target in vars_target.keys():
                    target_var_content = vars_target[target]
                    path = os.path.join(util.abs_path(target_vars_directory), target)
                    util.write_file(path, util.safe_dump(target_var_content))

    def _write_inventory(self):
        """
        Write the provisioner's inventory file to disk and returns None.

        :return: None
        """
        self._verify_inventory()

        util.write_file(self.inventory_file, util.safe_dump(self.inventory))

    def _remove_vars(self):
        """
        Remove hosts/host_vars/group_vars and returns None.

        :returns: None
        """
        for name in ("hosts", "group_vars", "host_vars"):
            d = os.path.join(self.inventory_directory, name)
            if os.path.islink(d) or os.path.isfile(d):
                os.unlink(d)
            elif os.path.isdir(d):
                shutil.rmtree(d)

    def _link_or_update_vars(self):
        """
        Create or updates the symlink to group_vars and returns None.

        :returns: None
        """
        for d, source in self.links.items():
            target = os.path.join(self.inventory_directory, d)
            source = os.path.join(self._config.scenario.directory, source)

            if not os.path.exists(source):
                msg = f"The source path '{source}' does not exist."
                util.sysexit_with_message(msg)
            msg = f"Inventory {source} linked to {target}"
            LOG.info(msg)
            os.symlink(source, target)

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
        return ansible_playbook.AnsiblePlaybook(
            playbook, self._config, verify, **kwargs
        )

    def _verify_inventory(self):
        """
        Verify the inventory is valid and returns None.

        :return: None
        """
        if not self.inventory:
            msg = "Instances missing from the 'platform' " "section of molecule.yml."
            util.sysexit_with_message(msg)

    def _get_config_template(self):
        """
        Return a config template string.

        :return: str
        """
        return """
{% for section, section_dict in config_options.items() -%}
[{{ section }}]
{% for k, v in section_dict.items() -%}
{{ k }} = {{ v }}
{% endfor -%}
{% endfor -%}
""".strip()

    def _vivify(self):
        """
        Return an autovivification default dict.

        :return: dict
        """
        return collections.defaultdict(self._vivify)

    def _default_to_regular(self, d):
        if isinstance(d, collections.defaultdict):
            d = {k: self._default_to_regular(v) for k, v in d.items()}

        return d

    def _get_plugin_directory(self) -> str:
        return os.path.join(self.directory, "plugins")

    def _get_modules_directories(self) -> List[str]:
        """Return list of ansilbe module includes directories.

        Adds modules directory from molecule and its plugins.
        """
        paths: List[Optional[str]] = []
        if os.environ.get("ANSIBLE_LIBRARY"):
            paths = list(map(util.abs_path, os.environ["ANSIBLE_LIBRARY"].split(":")))

        paths.append(
            util.abs_path(os.path.join(self._get_plugin_directory(), "modules"))
        )

        for d in drivers():
            p = d.modules_dir()
            if p:
                paths.append(p)
        paths.extend(
            [
                util.abs_path(
                    os.path.join(self._config.scenario.ephemeral_directory, "library")
                ),
                util.abs_path(os.path.join(self._config.project_directory, "library")),
                util.abs_path(
                    os.path.join(
                        os.path.expanduser("~"),
                        ".ansible",
                        "plugins",
                        "modules",
                    )
                ),
                "/usr/share/ansible/plugins/modules",
            ]
        )

        return [path for path in paths if path is not None]

    def _get_filter_plugin_directory(self):
        return util.abs_path(os.path.join(self._get_plugin_directory(), "filter"))

    def _absolute_path_for(self, env, key):
        return ":".join([self.abs_path(p) for p in env[key].split(":")])
