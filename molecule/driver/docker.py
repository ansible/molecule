#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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
from molecule.util import sysexit_with_message

log = logger.get_logger(__name__)


class Docker(base.Base):
    """
    The class responsible for managing `Docker`_ containers.  `Docker`_ is
    the default driver used in Molecule.

    Molecule leverages Ansible's `docker_container`_ module, by mapping
    variables from ``molecule.yml`` into ``create.yml`` and ``destroy.yml``.

    .. _`docker_container`: https://docs.ansible.com/ansible/latest/docker_container_module.html
    .. _`Docker Security Configuration`: https://docs.docker.com/engine/reference/run/#security-configuration

    .. code-block:: yaml

        driver:
          name: docker
        platforms:
          - name: instance
            hostname: instance
            image: image_name:tag
            dockerfile: Dockerfile.j2
            pull: True|False
            pre_build_image: True|False
            registry:
              url: registry.example.com
              credentials:
                username: $USERNAME
                password: $PASSWORD
                email: user@example.com
            override_command: True|False
            command: sleep infinity
            tty: True|False
            pid_mode: host
            privileged: True|False
            security_opts:
              - seccomp=unconfined
            volumes:
              - /sys/fs/cgroup:/sys/fs/cgroup:ro
            tmpfs:
              - /tmp
              - /run
            capabilities:
              - SYS_ADMIN
            exposed_ports:
              - 53/udp
              - 53/tcp
            published_ports:
              - 0.0.0.0:8053:53/udp
              - 0.0.0.0:8053:53/tcp
            ulimits:
              - nofile:262144:262144
            dns_servers:
              - 8.8.8.8
            networks:
              - name: foo
              - name: bar
            network_mode: host
            purge_networks: true
            docker_host: tcp://localhost:12376
            env:
              FOO: bar
            restart_policy: on-failure
            restart_retries: 1
            buildargs:
                http_proxy: http://proxy.example.com:8080/

    If specifying the `CMD`_ directive in your ``Dockerfile.j2`` or consuming a
    built image which declares a ``CMD`` directive, then you must set
    ``override_command: False``. Otherwise, Molecule takes care to honour the
    value of the ``command`` key or uses the default of ``bash -c "while true;
    do sleep 10000; done"`` to run the container until it is provisioned.

    When attempting to utilize a container image with `systemd`_ as your init
    system inside the container to simulate a real machine, make sure to set
    the ``privileged``, ``volume_mounts``, ``command``, and ``environment``
    values. An example using the ``centos:7`` image is below:

    .. note:: Do note that running containers in privileged mode is considerably
              less secure. For details, please reference `Docker Security
              Configuration`_

    .. code-block:: yaml

        platforms:
        - name: instance
          image: centos:7
          privileged: true
          volume_mounts:
            - "/sys/fs/cgroup:/sys/fs/cgroup:rw"
          command: "/usr/sbin/init"
          tty: True
          environment:
            container: docker

    .. code-block:: bash

        $ pip install molecule[docker]

    When pulling from a private registry, it is the user's discretion to decide
    whether to use hard-code strings or environment variables for passing
    credentials to molecule.

    .. important::

        Hard-coded credentials in ``molecule.yml`` should be avoided, instead use
        `variable substitution`_.

    Provide a list of files Molecule will preserve, relative to the scenario
    ephemeral directory, after any ``destroy`` subcommand execution.

    .. code-block:: yaml

        driver:
          name: docker
          safe_files:
            - foo

    .. _`Docker`: https://www.docker.com
    .. _`systemd`: https://www.freedesktop.org/wiki/Software/systemd/
    .. _`CMD`: https://docs.docker.com/engine/reference/builder/#cmd
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
        return ('docker exec '
                '-e COLUMNS={columns} '
                '-e LINES={lines} '
                '-e TERM=bash '
                '-e TERM=xterm '
                '-ti {instance} bash')

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

    def sanity_checks(self):
        """Implement Docker driver sanity checks."""

        if self._config.state.sanity_checked:
            return

        log.info("Sanity checks: '{}'".format(self._name))

        HAS_DOCKER_PY = None
        try:
            from ansible.module_utils.docker_common import HAS_DOCKER_PY
        except ImportError:

            # ansible 2.8+
            try:
                from ansible.module_utils.docker.common import HAS_DOCKER_PY
            except ImportError:
                pass

        if not HAS_DOCKER_PY:
            msg = ('Missing Docker driver dependency. Please '
                   "install via 'molecule[docker]' or refer to "
                   'your INSTALL.rst driver documentation file')
            sysexit_with_message(msg)

        try:
            import docker
            import requests
            docker_client = docker.from_env()
            docker_client.ping()
        except requests.exceptions.ConnectionError:
            msg = ('Unable to contact the Docker daemon. '
                   'Please refer to https://docs.docker.com/config/daemon/ '
                   'for managing the daemon')
            sysexit_with_message(msg)

        self._config.state.change_state('sanity_checked', True)
