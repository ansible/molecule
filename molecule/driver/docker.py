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

from __future__ import absolute_import

import os

from molecule import logger
from molecule.driver import base

LOG = logger.get_logger(__name__)


class Docker(base.Base):
    """
    The class responsible for managing `Docker`_ containers.  `Docker`_ is
    the default driver used in Molecule.

    Molecule leverages Ansible's `docker_container`_ module, by mapping
    variables from `molecule.yml` into `create.yml` and `destroy.yml`.

    .. _`docker_container`: http://docs.ansible.com/ansible/latest/docker_container_module.html

    .. code-block:: yaml

        driver:
          name: docker
        platforms:
          - name: instance
            hostname: instance
            image: image_name:tag
            registry:
              url: registry.example.com
            command: sleep infinity
            privileged: "{{ item.privileged | default(omit) }}"
            volumes:
              - /sys/fs/cgroup:/sys/fs/cgroup:ro
            capabilities:
              - SYS_ADMIN
            exposed_ports:
              - "53/udp"
              - "53/tcp"
            published_ports:
              - "0.0.0.0:8053:53/udp"
              - "0.0.0.0:8053:53/tcp"
            ulimits: "{{ item.ulimits | default(omit) }}"
            dns_servers: "{{ item.dns_servers | default(omit) }}"
            networks:
              - name: foo
              - name: bar

    .. code-block:: bash

        $ sudo pip install docker-py

    Provide the files Molecule will preserve upon each subcommand execution.

    .. code-block:: yaml

        driver:
          name: docker
          safe_files:
            - foo
            - .molecule/bar

    .. _`Docker`: https://www.docker.com
    """  # noqa

    def __init__(self, config):
        super(Docker, self).__init__(config)
        self._name = 'docker'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def login_cmd_template(self):
        return 'docker exec -ti {instance} bash'

    @property
    def default_safe_files(self):
        return [
            os.path.join(self._config.scenario.ephemeral_directory,
                         'Dockerfile')
        ]

    @property
    def default_ssh_connection_options(self):
        return []

    def login_options(self, instance_name):
        return {'instance': instance_name}

    def ansible_connection_options(self, instance_name):
        return {'ansible_connection': 'docker'}
