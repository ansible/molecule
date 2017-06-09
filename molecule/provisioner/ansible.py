#  Copyright (c) 2015-2017 Cisco Systems, Inc.

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

import copy
import collections
import os
import shutil

from molecule import logger
from molecule import util
from molecule.provisioner import base
from molecule.provisioner import ansible_playbook

LOG = logger.get_logger(__name__)


class Namespace(object):
    def __init__(self, config):
        """
        A class to act as a module to namespace playbook properties.

        :param config: An instance of a Molecule config.
        :return: None
        """
        self._config = config

    @property
    def setup(self):
        return self._get_ansible_playbook('setup')

    @property
    def converge(self):
        c = self._config.config

        return os.path.join(self._config.scenario.directory,
                            c['provisioner']['playbooks']['converge'])

    @property
    def teardown(self):
        return self._get_ansible_playbook('teardown')

    def _get_ansible_playbook(self, section):
        c = self._config.config
        driver_dict = c['provisioner']['playbooks'].get(
            self._config.driver.name)

        if driver_dict:
            playbook = driver_dict[section]
        else:
            playbook = c['provisioner']['playbooks'][section]

        return os.path.join(self._config.scenario.directory, playbook)


class Ansible(base.Base):
    """
    `Ansible`_ is the default provisioner.  No other provisioner will be
    supported.

    Molecule's provisioner manages the instances lifecycle.  However, the user
    must provide the setup, teardown, and converge playbooks.  Molecule's
    `init` subcommand will provide the necessary files for convenience.

    .. important::

        Reserve the setup and teardown playbooks for provisioning.  Do not
        attempt to gather facts or perform operations on the provisioned nodes
        inside these playbooks.  Due to the gymnastics necessary to sync state
        between Ansible and Molecule, it is best to perform these tasks in the
        converge playbook.

        It is the developers responsiblity to properly map the modules's fact
        data into the instance_conf_dict fact in the setup playbook.  This
        allows Molecule to properly configure Ansible inventory.

    Additional options can be passed to `ansible-playbook` through the options
    dict.  Any option set in this section will override the defaults.

    .. code-block:: yaml

        provisioner:
          name: ansible
          options:
            vvv: True
          playbooks:
            setup: create.yml
            converge: playbook.yml
            teardown: destroy.yml

    Share playbooks between roles.

    .. code-block:: yaml

        provisioner:
          name: ansible
          playbooks:
            setup: ../default/create.yml
            teardown: ../default/destroy.yml
            converge: playbook.yml

    Multiple driver playbooks.  In some situations a developer may choose to
    test the same role against different backends.  Molecule will choose driver
    specific setup/teardown playbooks, if the determined driver has a key in
    the playbooks section of the provisioner's dict.

    .. important::

        If the determined driver has a key in the playbooks dict, Molecule will
        use this dict to resolve all provisioning playbooks (setup/teardown).

    .. code-block:: yaml

        provisioner:
          name: ansible
          playbooks:
            docker:
              setup: create.yml
              teardown: destroy.yml
            setup: create.yml
            teardown: destroy.yml
            converge: playbook.yml

    Environment variables can be passed to the provisioner.

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

    Roles which require host/groups to have certain variables set.  Molecule
    uses the same `variables defined in a playbook`_ syntax as `Ansible`_.

    .. code-block:: yaml

        provisioner:
          name: ansible
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

    Override connection options:

    .. code-block:: yaml

        provisioner:
          name: ansible
          connection_options:
            ansible_ssh_user: foo
            ansible_ssh_common_args: -o IdentitiesOnly=no

    .. _`variables defined in a playbook`: http://docs.ansible.com/ansible/playbooks_variables.html#variables-defined-in-a-playbook
    """  # noqa

    def __init__(self, config):
        """
        A class encapsulating the provisioner.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(Ansible, self).__init__(config)
        self._ns = Namespace(config)

    @property
    def default_config_options(self):
        """
        Default options provided to construct ansible.cfg and returns a dict.

        :return: dict
        """
        envs = self._config.config['provisioner']['env']

        roles_path = '../../../../'
        filter_plugins = self._get_filter_plugin_directory()
        library = self._get_libraries_directory()

        # ANSIBLE_ like environments set on command line have higher precedence
        # than their equivalents in the ansible.cfg file.
        # Use env value instead of the env itself.
        try:
             roles_path = '{}:{}'.format(roles_path, envs['ANSIBLE_ROLES_PATH'])
        except KeyError:
             pass

        try:
             filter_plugins = '{}:{}'.format(filter_plugins, envs['ANSIBLE_FILTER_PLUGINS'])
        except KeyError:
             pass

        try:
             library = '{}:{}'.format(library, envs['ANSIBLE_LIBRARY'])
        except KeyError:
             pass

        return {
            'defaults': {
                'ansible_managed':
                'Ansible managed: Do NOT edit this file manually!',
                'retry_files_enabled': False,
                'host_key_checking': False,
                'nocows': 1,
                'roles_path': roles_path,
                'library': library,
                'filter_plugins': filter_plugins,
            },
            'ssh_connection': {
                'scp_if_ssh': True,
            },
        }

    @property
    def default_options(self):
        d = {}
        if self._config.args.get('debug'):
            d['vvv'] = True

        return d

    @property
    def default_env(self):
        env = self._config.merge_dicts(os.environ.copy(), self._config.env)
        env = self._config.merge_dicts(
            env, {'ANSIBLE_CONFIG': self._config.provisioner.config_file})
        env = self._config.merge_dicts(env, self._config.env)

        return env

    @property
    def name(self):
        return self._config.config['provisioner']['name']

    @property
    def config_options(self):
        return self._config.merge_dicts(
            self.default_config_options,
            self._config.config['provisioner']['config_options'])

    @property
    def options(self):
        return self._config.merge_dicts(
            self.default_options,
            self._config.config['provisioner']['options'])

    @property
    def env(self):
        envs = self._config.merge_dicts(
            self.default_env, self._config.config['provisioner']['env'])
        if 'ANSIBLE_FILTER_PLUGINS' in envs:
            del envs['ANSIBLE_FILTER_PLUGINS']
        if 'ANSIBLE_ROLES_PATH' in envs:
            del envs['ANSIBLE_ROLES_PATH']
        if 'ANSIBLE_LIBRARY' in envs:
            del envs['ANSIBLE_LIBRARY']
        return envs

    @property
    def host_vars(self):
        return self._config.config['provisioner']['host_vars']

    @property
    def group_vars(self):
        return self._config.config['provisioner']['group_vars']

    @property
    def inventory(self):
        """
        Create an inventory structure and returns a dict.

        .. code-block:: yaml
            ungrouped:
              vars:
                foo: bar
              hosts:
                instance-1-default:
                instance-2-default:
              children:
                $child_group_name:
                  hosts:
                    instance-1-default:
                    instance-2-default:
            $group_name:
              hosts:
                instance-1-default:
                  ansible_connection: docker
                instance-2-default:
                  ansible_connection: docker

        :return: str
        """
        dd = self._vivify()
        for platform in self._config.platforms.instances_with_scenario_name:
            for group in platform.get('groups', ['ungrouped']):
                instance_name = platform['name']
                connection_options = self.connection_options(instance_name)
                dd['all']['hosts'][instance_name] = connection_options
                dd[group]['hosts'][instance_name] = connection_options
                # Ungrouped
                dd['ungrouped']['vars'] = {}
                # Children
                for child_group in platform.get('children', []):
                    dd[group]['children'][child_group]['hosts'][
                        instance_name] = connection_options

        return self._default_to_regular(dd)

    @property
    def inventory_file(self):
        return os.path.join(self._config.scenario.ephemeral_directory,
                            'ansible_inventory.yml')

    @property
    def config_file(self):
        return os.path.join(self._config.scenario.ephemeral_directory,
                            'ansible.cfg')

    @property
    def playbooks(self):
        return self._ns

    def connection_options(self, instance_name):
        d = self._config.driver.ansible_connection_options(instance_name)

        return self._config.merge_dicts(
            d, self._config.config['provisioner']['connection_options'])

    def check(self):
        """
        Executes `ansible-playbook` against the converge playbook with the
        ``--check`` flag and returns None.

        :return: None
        """
        pb = self._get_ansible_playbook(self.playbooks.converge)
        pb.add_cli_arg('check', True)
        pb.execute()

    def converge(self, playbook=None, **kwargs):
        """
        Executes `ansible-playbook` against the converge playbook unless
        specified otherwise and returns a string.

        :param playbook: An optional string containing an absolute path to a
         playbook.
        :param kwargs: An optional keyword arguments.
        :return: str
        """
        if playbook is None:
            pb = self._get_ansible_playbook(self.playbooks.converge, **kwargs)
        else:
            pb = self._get_ansible_playbook(playbook, **kwargs)

        return pb.execute()

    def destroy(self):
        """
        Executes `ansible-playbook` against the destroy playbook and returns
        None.

        :return: None
        """
        pb = self._get_ansible_playbook(self.playbooks.teardown)
        pb.execute()

    def setup(self):
        """
        Executes `ansible-playbook` against the setup playbook and returns
        None.

        :return: None
        """
        pb = self._get_ansible_playbook(self.playbooks.setup)
        pb.execute()

    def syntax(self):
        """
        Executes `ansible-playbook` against the converge playbook with the
        ``-syntax-check`` flag and returns None.

        :return: None
        """
        pb = self._get_ansible_playbook(self.playbooks.converge)
        pb.add_cli_arg('syntax-check', True)
        pb.execute()

    def write_inventory(self):
        """
        Writes the provisioner's inventory file to disk and returns None.

        :return: None
        """
        self._verify_inventory()

        util.write_file(self.inventory_file, util.safe_dump(self.inventory))

    def write_config(self):
        """
        Writes the provisioner's config file to disk and returns None.

        :return: None
        """
        # self._verify_config()

        template = util.render_template(
            self._get_config_template(), config_options=self.config_options)
        util.write_file(self.config_file, template)

    def add_or_update_vars(self, target):
        """
        Creates host and/or group vars and returns None.

        :param target: A string containing either `host_vars` or `group_vars`.
        :returns: None
        """
        if target == 'host_vars':
            vars_target = copy.deepcopy(self.host_vars)
            # Append the scenario-name
            for instance_name, _ in self.host_vars.items():
                if instance_name == 'localhost':
                    instance_key = instance_name
                else:
                    instance_key = util.instance_with_scenario_name(
                        instance_name, self._config.scenario.name)

                vars_target[instance_key] = vars_target.pop(instance_name)

        elif target == 'group_vars':
            vars_target = self.group_vars

        if not vars_target:
            return

        ephemeral_directory = self._config.scenario.ephemeral_directory
        target_vars_directory = os.path.join(ephemeral_directory, target)

        if not os.path.isdir(os.path.abspath(target_vars_directory)):
            os.mkdir(os.path.abspath(target_vars_directory))

        for target in vars_target.keys():
            target_var_content = vars_target[target]
            path = os.path.join(os.path.abspath(target_vars_directory), target)
            util.write_file(path, util.safe_dump(target_var_content))

    def remove_vars(self):
        """
        Remove host and/or group vars and returns None.

        :returns: None
        """
        gv = os.path.join(self._config.scenario.ephemeral_directory,
                          'group_vars')
        hv = os.path.join(self._config.scenario.ephemeral_directory,
                          'host_vars')

        if os.path.exists(gv):
            shutil.rmtree(gv)
        if os.path.exists(hv):
            shutil.rmtree(hv)

    def _get_ansible_playbook(self, playbook, **kwargs):
        """
        Get an instance of AnsiblePlaybook and returns it.

        :param playbook: A string containing an absolute path to a
         provisioner's playbook.
        :param kwargs: An optional keyword arguments.
        :return: object
        """
        return ansible_playbook.AnsiblePlaybook(self.inventory_file, playbook,
                                                self._config, **kwargs)

    def _verify_inventory(self):
        """
        Verify the inventory is valid and returns None.

        :return: None
        """
        if not self.inventory:
            msg = ("Instances missing from the 'platform' "
                   "section of molecule.yml.")
            util.sysexit_with_message(msg)

    def _get_config_template(self):
        """
        Returns a config template string.

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

    def _get_plugin_directory(self):
        return os.path.join(
            os.path.dirname(__file__), '..', '..', 'molecule', 'provisioner',
            'ansible', 'plugins')

    def _get_libraries_directory(self):
        return os.path.join(self._get_plugin_directory(), 'libraries')

    def _get_filter_plugin_directory(self):
        return os.path.join(self._get_plugin_directory(), 'filters')
