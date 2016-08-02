#  Copyright (c) 2015-2016 Cisco Systems
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import collections
import io
import json

import docker

from molecule import utilities
from molecule.provisioners import baseprovisioner


class DockerProvisioner(baseprovisioner.BaseProvisioner):
    def __init__(self, molecule):
        super(DockerProvisioner, self).__init__(molecule)
        self._docker = docker.from_env(assert_hostname=False)
        self._containers = self.molecule.config.config['docker']['containers']
        self._provider = self._get_provider()
        self._platform = self._get_platform()
        self.status()

        self.image_tag = 'molecule_local/{}:{}'

        if 'install_python' not in self.molecule.config.config['docker']:
            self.molecule.config.config['docker']['install_python'] = True

    def _get_platform(self):
        return 'Docker'

    def _get_provider(self):
        return 'Docker'

    @property
    def name(self):
        return 'docker'

    @property
    def instances(self):
        return self._containers

    @property
    def default_provider(self):
        pass

    @property
    def default_platform(self):
        pass

    @property
    def provider(self):
        pass

    @property
    def platform(self):
        pass

    @platform.setter
    def platform(self, val):
        return

    @property
    def valid_providers(self):
        return [{'name': 'Docker'}]

    @property
    def valid_platforms(self):
        return [{'name': 'Docker'}]

    @property
    def ssh_config_file(self):
        return None

    @property
    def ansible_connection_params(self):
        params = {'user': 'root', 'connection': 'docker'}

        return params

    def build_image(self):
        available_images = [tag.encode('utf-8')
                            for image in self._docker.images()
                            for tag in image.get('RepoTags')]

        for container in self.instances:

            if 'install_python' in container and container[
                    'install_python'] is False:
                continue
            else:
                utilities.print_info(
                    "Creating Ansible compatible image of {}:{} ...".format(
                        container['image'], container['image_version']))

            if 'registry' in container:
                container['registry'] += '/'
            else:
                container['registry'] = ''

            dockerfile = '''
            FROM {}:{}
            RUN bash -c 'if [ -x "$(command -v apt-get)" ]; then apt-get update && apt-get install -y python sudo; fi'
            RUN bash -c 'if [ -x "$(command -v yum)" ]; then yum makecache fast && yum update -y && yum install -y python sudo; fi'

            '''  # noqa

            dockerfile = dockerfile.format(
                container['registry'] + container['image'],
                container['image_version'])

            f = io.BytesIO(dockerfile.encode('utf-8'))

            container['image'] = container['registry'].replace(
                '/', '_').replace(':', '_') + container['image']
            tag_string = self.image_tag.format(container['image'],
                                               container['image_version'])

            errors = False

            if tag_string not in available_images:
                utilities.print_info('Building ansible compatible image ...')
                previous_line = ''
                for line in self._docker.build(fileobj=f, tag=tag_string):
                    for line_split in line.split('\n'):
                        if len(line_split) > 0:
                            line = json.loads(line_split)
                            if 'stream' in line:
                                utilities.logger.warning('\t{}'.format(line[
                                    'stream']))
                            if 'errorDetail' in line:
                                utilities.logger.warning('\t{}'.format(line[
                                    'errorDetail']['message']))
                                errors = True
                            if 'status' in line:
                                if previous_line not in line['status']:
                                    utilities.logger.warning('\t{} ...'.format(
                                        line['status']))
                                previous_line = line['status']

                if errors:
                    utilities.logger.error('Build failed for {}'.format(
                        tag_string))
                    return
                else:
                    utilities.print_success('Finished building {}'.format(
                        tag_string))

    def up(self, no_provision=True):
        if self.molecule.config.config['docker']['install_python']:
            self.build_image()
        else:
            self.image_tag = '{}:{}'

        for container in self.instances:

            if 'privileged' not in container:
                container['privileged'] = False

            if 'port_bindings' not in container:
                container['port_bindings'] = {}

            if 'volume_mounts' not in container:
                container['volume_mounts'] = []

            if 'command' not in container:
                container['command'] = ""

            docker_host_config = self._docker.create_host_config(
                privileged=container['privileged'],
                port_bindings=container['port_bindings'],
                binds=container['volume_mounts'])

            if (container['Created'] is not True):
                utilities.logger.warning(
                    'Creating container {} with base image {}:{} ...'.format(
                        container['name'], container['image'],
                        container['image_version']), )
                container = self._docker.create_container(
                    image=self.image_tag.format(container['image'],
                                                container['image_version']),
                    tty=True,
                    detach=False,
                    name=container['name'],
                    ports=container['port_bindings'].keys(),
                    host_config=docker_host_config,
                    command=container['command'])
                self._docker.start(container=container.get('Id'))
                container['Created'] = True

                utilities.print_success('Container created.\n')
            else:
                self._docker.start(container['name'])
                utilities.print_success('Starting container {}...'.format(
                    container['name']))

    def destroy(self):
        for container in self.instances:
            if (container['Created']):
                utilities.logger.warning('Stopping container {} ...'.format(
                    container['name']))
                self._docker.stop(container['name'], timeout=0)
                self._docker.remove_container(container['name'])
                utilities.print_success('Removed container {}.\n'.format(
                    container['name']))
                container['Created'] = False

    def status(self):
        Status = collections.namedtuple('Status', ['name', 'state', 'provider',
                                                   'ports'])
        instance_names = [x['name'] for x in self.instances]
        created_containers = self._docker.containers(all=True)
        created_container_names = []
        status_list = []

        for container in created_containers:
            container_name = container.get('Names')[0][1:].encode('utf-8')
            ports = container.get('Ports')
            created_container_names.append(container_name)
            if container_name in instance_names:
                status_list.append(Status(name=container_name,
                                          state=container.get('Status'),
                                          provider='docker',
                                          ports=ports))

        # Check the created status of all the tracked instances
        for container in self.instances:
            if container['name'] in created_container_names:
                container['Created'] = True
            else:
                container['Created'] = False
                status_list.append(Status(name=container['name'],
                                          state="Not Created",
                                          provider='docker',
                                          ports=[]))

        return status_list

    def conf(self, vm_name=None, ssh_config=False):
        pass

    def inventory_entry(self, instance):
        template = '{} connection=docker\n'

        return template.format(instance['name'])

    def login_cmd(self, instance):
        return 'docker exec -ti {} bash'

    def login_args(self, instance):
        return [instance]

    @property
    def testinfra_args(self):
        kwargs = {'connection': 'docker'}

        return kwargs

    @property
    def serverspec_args(self):
        return dict()
