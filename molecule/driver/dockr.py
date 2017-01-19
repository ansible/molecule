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

from molecule.driver import base


class Dockr(base.Base):
    """
    `Docker`_ is the default driver.

    .. code-block:: yaml

        driver:
          name: docker

    .. code-block:: bash

        $ pip install docker-py

    .. _`Docker`: https://www.docker.com
    """

    def __init__(self, config):
        super(Dockr, self).__init__(config)

    @property
    def testinfra_options(self):
        return {'connection': 'docker'}

    @property
    def connection_options(self):
        return {'ansible_connection': 'docker'}

    @property
    def login_cmd_template(self):
        return 'docker exec -ti {} bash'

    def login_args(self, instance):
        return [instance]

    def status(self):
        status_list = []
        for platform in self._config.platforms.instances_with_scenario_name:
            instance_name = platform['name']
            driver_name = self.name.capitalize()
            provisioner_name = self._config.provisioner.name.capitalize()
            scenario_name = self._config.scenario.name
            state = self._instances_state()

            status_list.append(
                base.Status(
                    instance_name=instance_name,
                    driver_name=driver_name,
                    provisioner_name=provisioner_name,
                    scenario_name=scenario_name,
                    state=state))

        return status_list

    def _instances_state(self):
        """
        Get instances state and returns a string.

        .. important::

            Molecule assumes all instances were created successfully by
            Ansible, otherwise Ansible would return an error on create.  This
            may prove to be a bad assumption.  However, configuring Moleule's
            driver to match the options passed to the playbook may prove
            difficult.  Especially in cases where the user is provisioning
            instances off localhost.
        """
        if self._config.state.created:
            return 'Created'
        else:
            return 'Not Created'
