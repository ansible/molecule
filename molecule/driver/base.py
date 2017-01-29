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

import abc
import collections
import os

Status = collections.namedtuple('Status', [
    'instance_name', 'driver_name', 'provisioner_name', 'scenario_name',
    'state'
])


class Base(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        """
        Base initializer for all :ref:`Driver` classes.

        :param config: An instance of a Molecule config.
        :returns: None
        """
        self._config = config

    @property
    def testinfra_options(self):
        """
        Testinfra specific options and returns a dict.

        :returns: dict
        """
        return {
            'connection': 'ansible',
            'ansible-inventory': '.molecule/ansible_inventory.yml'
        }

    @abc.abstractproperty
    def login_cmd_template(self):
        """
        The login command template to be populated by `login_args` and
        returns a string.

        :returns: str
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def safe_files(self):
        """
        Generated files to be preserved and returns a list.

        :returns: list
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def login_args(self, instance_name):
        """
        Arguments used in the login command and returns a list.

        :param instance_name: A string containing the instance to login to.
        :returns: list
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def connection_options(self, instance_name):
        """
        Connection options supplied to inventory and returns a dict.

        :param instance_name: A string containing the instance to login to.
        :returns: str
        """
        pass  # pragma: no cover

    @property
    def name(self):
        return self._config.config['driver']['name']

    @property
    def options(self):
        return self._config.config['driver']['options']

    @property
    def instance_config(self):
        return os.path.join(self._config.ephemeral_directory,
                            'instance_config.yml')

    def status(self):
        """
        Collects the instances state and returns a list.

        .. important::

            Molecule assumes all instances were created successfully by
            Ansible, otherwise Ansible would return an error on create.  This
            may prove to be a bad assumption.  However, configuring Moleule's
            driver to match the options passed to the playbook may prove
            difficult.  Especially in cases where the user is provisioning
            instances off localhost.
        :returns: list
        """
        status_list = []
        for platform in self._config.platforms.instances_with_scenario_name:
            instance_name = platform['name']
            driver_name = self.name.capitalize()
            provisioner_name = self._config.provisioner.name.capitalize()
            scenario_name = self._config.scenario.name
            state = self._instances_state()

            status_list.append(
                Status(
                    instance_name=instance_name,
                    driver_name=driver_name,
                    provisioner_name=provisioner_name,
                    scenario_name=scenario_name,
                    state=state))

        return status_list

    def _instances_state(self):
        """
        Get instances state and returns a string.

        :returns: str
        """
        if self._config.state.created:
            return 'Created'
        else:
            return 'Not Created'
