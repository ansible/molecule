#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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
import io
import json
import sys

try:
    import docker
except ImportError:  # pragma: no cover
    sys.exit(
        'ERROR: python docker driver missing, install the docker package.')

from molecule import util
from molecule.driver import basedriver


class DockerDriver(basedriver.BaseDriver):
    def __init__(self, molecule):
        super(DockerDriver, self).__init__(molecule)
        self._docker = docker.APIClient(
            version='auto', **docker.utils.kwargs_from_env())
        self._containers = self.molecule.config.config['docker']['containers']
        self._provider = self._get_provider()
        self._platform = self._get_platform()

        self.image_tag = 'molecule_local/{}:{}'

        if 'build_image' not in self.molecule.config.config['docker']:
            self.molecule.config.config['docker']['build_image'] = True

    @property
    def name(self):
        return 'docker'

    @property
    def instances(self):
        created_containers = self._docker.containers(all=True)
        created_container_names = [
            container.get('Names')[0][1:].encode('utf-8')
            for container in created_containers
        ]
        for container in self._containers:
            if container.get('name') in created_container_names:
                container['created'] = True
            else:
                container['created'] = False

        return self._containers

    @property
    def default_provider(self):
        return self._provider

    @property
    def default_platform(self):
        return self._platform

    @property
    def provider(self):
        return self._provider

    @property
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, val):
        self._platform = val

    @property
    def valid_providers(self):
        return [{'name': self.provider}]

    @property
    def valid_platforms(self):
        return [{'name': self.platform}]

    @property
    def ssh_config_file(self):
        return

    @property
    def ansible_connection_params(self):
        return {'user': 'root', 'connection': 'docker'}

    @property
    def testinfra_args(self):
        return {'connection': 'docker'}

    @property
    def serverspec_args(self):
        return {}

    def up(self, no_provision=True):
        self.molecule.state.change_state('driver', self.name)
        if self.molecule.config.config['docker']['build_image']:
            self._build_ansible_compatible_image()
        else:
            self.image_tag = '{}:{}'

        for container in self.instances:
            privileged = container.get('privileged', False)
            port_bindings = container.get('port_bindings', {})
            volume_mounts = container.get('volume_mounts', [])
            links = container.get('links', {})
            network_mode = container.get('network_mode', '')
            cap_add = container.get('cap_add', [])
            cap_drop = container.get('cap_drop', [])
            command = container.get('command', '')
            environment = container.get('environment')

            docker_host_config = self._docker.create_host_config(
                privileged=privileged,
                port_bindings=port_bindings,
                binds=volume_mounts,
                links=links,
                network_mode=network_mode,
                cap_add=cap_add,
                cap_drop=cap_drop)

            if (container['created'] is not True):
                msg = ('Creating container {} '
                       'with base image {}:{}...').format(
                           container['name'], container['image'],
                           container['image_version'])
                util.print_warn(msg)
                container = self._docker.create_container(
                    image=self.image_tag.format(container['image'],
                                                container['image_version']),
                    tty=True,
                    detach=False,
                    name=container['name'],
                    ports=port_bindings.keys(),
                    host_config=docker_host_config,
                    environment=environment,
                    command=command)
                self._docker.start(container=container.get('Id'))
                container['created'] = True

                util.print_success('Container created.')
            else:
                self._docker.start(container['name'])
                msg = 'Starting container {}...'.format(container['name'])
                util.print_info(msg)

    def destroy(self):
        for container in self.instances:
            if (container['created']):
                msg = 'Stopping container {}...'.format(container['name'])
                util.print_warn(msg)
                self._docker.stop(container['name'], timeout=0)
                self._docker.remove_container(container['name'])
                msg = 'Removed container {}.'.format(container['name'])
                util.print_success(msg)
                container['created'] = False

    def status(self):
        Status = collections.namedtuple(
            'Status', ['name', 'state', 'provider', 'ports'])
        status_list = []
        for container in self.instances:
            name = container.get('name')
            try:
                d = self._docker.containers(filters={'name': name})[0]
                state = d.get('Status')
                ports = d.get('Ports')
            except IndexError:
                state = 'not_created'
                ports = []
            status_list.append(
                Status(
                    name=name,
                    state=state,
                    provider=self.provider,
                    ports=ports))

        return status_list

    def conf(self, vm_name=None, ssh_config=False):
        pass

    def inventory_entry(self, instance):
        template = '{} ansible_connection=docker\n'

        return template.format(instance['name'])

    def login_cmd(self, instance):
        return 'docker exec -ti {} bash'

    def login_args(self, instance):
        return [instance]

    def _get_platform(self):
        return 'docker'

    def _get_provider(self):
        return 'docker'

    def _build_ansible_compatible_image(self):
        available_images = [
            tag.encode('utf-8')
            for image in self._docker.images() if image.get('RepoTags') is not None
            for tag in image.get('RepoTags')
        ]

        for container in self.instances:
            if container.get('build_image'):
                msg = ('Creating Ansible compatible '
                       'image of {}:{} ...').format(container['image'],
                                                    container['image_version'])
                util.print_info(msg)

            if 'registry' in container:
                container['registry'] += '/'
            else:
                container['registry'] = ''

            dockerfile = '''
            FROM {container_image}:{container_version}
            {container_environment}
            RUN bash -c 'if [ -x "$(command -v apt-get)" ]; then apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python sudo; fi'
            RUN bash -c 'if [ -x "$(command -v yum)" ]; then yum makecache fast && yum update -y && yum install -y python sudo yum-plugin-ovl && sed -i 's/plugins=0/plugins=1/g' /etc/yum.conf; fi'
            RUN bash -c 'if [ -x "$(command -v zypper)" ]; then zypper refresh && zypper update -y && zypper install -y python sudo; fi'

            '''  # noqa

            if 'dockerfile' in container:
                dockerfile = container['dockerfile']
                f = io.open(dockerfile)

            else:
                environment = container.get('environment')
                if environment:
                    environment = '\n'.join(
                        'ENV {} {}'.format(k, v)
                        for k, v in environment.iteritems())
                else:
                    environment = ''

                dockerfile = dockerfile.format(
                    container_image=container['registry'] + container['image'],
                    container_version=container['image_version'],
                    container_environment=environment)

                f = io.BytesIO(dockerfile.encode('utf-8'))

                container['image'] = container['registry'].replace(
                    '/', '_').replace(':', '_') + container['image']

            tag_string = self.image_tag.format(container['image'],
                                               container['image_version'])

            errors = False

            if tag_string not in available_images or 'dockerfile' in container:
                util.print_info('Building ansible compatible image...')
                previous_line = ''
                for line in self._docker.build(fileobj=f, tag=tag_string):
                    for line_split in line.split('\n'):
                        if len(line_split) > 0:
                            line = json.loads(line_split)
                            if 'stream' in line:
                                msg = '\t{}'.format(line['stream'])
                                util.print_warn(msg)
                            if 'errorDetail' in line:
                                ed = line['errorDetail']['message']
                                msg = '\t{}'.format(ed)
                                util.print_warn(msg)
                                errors = True
                            if 'status' in line:
                                if previous_line not in line['status']:
                                    msg = '\t{} ...'.format(line['status'])
                                    util.print_warn(msg)
                                previous_line = line['status']

                if errors:
                    msg = 'Build failed for {}.'.format(tag_string)
                    util.print_error(msg)
                    return
                else:
                    util.print_success('Finished building {}.'.format(
                        tag_string))
