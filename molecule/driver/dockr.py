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

import collections
import sys

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
        docker = self._delayed_import()
        self._docker = docker.Client(
            version='auto', **docker.utils.kwargs_from_env())

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
        Status = collections.namedtuple('Status', ['name', 'state', 'driver'])
        status_list = []
        for platform in self._config.platforms_with_scenario_name:
            instance_name = platform['name']
            try:
                d = self._docker.containers(filters={'name': instance_name})[0]
                state = d.get('Status')
            except IndexError:
                state = 'Not Created'
            status_list.append(
                Status(
                    name=instance_name,
                    state=state,
                    driver=self.name.capitalize()))

        return status_list

    def _delayed_import(self):
        try:
            import docker

            return docker
        except ImportError:  # pragma: no cover
            sys.exit('ERROR: Driver missing, install docker-py.')
