#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import os
import sys

import molecule
import molecule.config
import molecule.util

try:
    import vagrant
except ImportError:
    sys.exit('ERROR: Driver missing, install python-vagrant.')

DOCUMENTATION = '''
---
module: vagrant
short_description: Manage Vagrant instances
description:
  - Manage the life cycle of Vagrant instances.
  - Supports check mode. Run with --check and --diff to view config difference,
    and list of actions to be taken.
version_added: 2.0
author:
  - Cisco Systems, Inc.
options:
  instance_name:
    description:
      - Assign a name to a new instance or match an existing instance.
    required: True
    default: None
  instance_interfaces:
    description:
      - Assign interfaces to a new instance.
    required: False
    default: []
  instance_raw_config_args:
    description:
      - Additional Vagrant options not explcitly exposed by this module.
    required: False
    default: None
  platform_box:
    description:
      - Name of Vagrant box.
    required: True
    default: None
  platform_box_version:
    description:
      - Explicit version of Vagrant box to use.
    required: False
    default: None
  platform_box_url:
    description:
      - The URL to a Vagrant box.
    required: False
    default: None
  provider_name:
    description:
      - Name of the Vagrant provider to use.
    required: False
    default: virtualbox
  provider_memory:
    description:
      - Ammount of memory to allocate to the instance.
    required: False
    default: 512
  provider_cpus:
    description:
      - Number of CPUs to allocate to the instance.
    required: False
    default: 2
  provider_options:
    description:
      - Additional provider options not explcitly exposed by this module.
    required: False
    default: {}
  provider_raw_config_args:
    description:
      - Additional Vagrant options not explcitly exposed by this module.
    required: False
    default: None
  force_stop:
    description:
      - Force halt the instance, then destroy the instance.
    required: False
    default: False
  state:
    description:
      - The desired state of the instance.
    required: True
    choices: ['up', 'destroy']
    default: None
requirements:
    - python >= 2.6
    - python-vagrant
    - vagrant
'''

EXAMPLES = '''
See doc/source/configuration.rst
'''

VAGRANTFILE_TEMPLATE = '''
require 'yaml'

Vagrant.configure('2') do |config|
  vagrant_config = YAML::load_file('{{ vagrantfile_config }}')

  if Vagrant.has_plugin?('vagrant-cachier')
    config.cache.scope = 'machine'
  end

  ##
  # Platforms
  ##
  if vagrant_config['platform']
    platform = vagrant_config['platform']
    config.vm.box = platform['box']

    if platform['box_version']
      config.vm.box_version = platform['box_version']
    end

    if platform['box_url']
      config.vm.box_url = platform['box_url']
    end
  end

  ##
  # Provider
  ##
  if vagrant_config['provider']
    provider = vagrant_config['provider']

    # Boot time optimization
    if provider['options']
      if provider['options']['synced_folder']
        config.vm.synced_folder provider['options']['synced_folder']
      else
        config.vm.synced_folder ".", "/vagrant", disabled: true
      end

      if provider['options']['ssh_insert_key']
        config.ssh.insert_key = true
      else
        config.ssh.insert_key = false
      end
    else
      config.vm.synced_folder ".", "/vagrant", disabled: true
      config.ssh.insert_key = true
    end

    ##
    # Virtualbox
    ##
    if provider['name'] == 'virtualbox'
      config.vm.provider provider['name'] do |virtualbox|
        virtualbox.memory = provider['options']['memory']
        virtualbox.cpus = provider['options']['cpus']

        if provider['options'] && provider['options']['linked_clone']
          if Gem::Version.new(Vagrant::VERSION) >= Gem::Version.new('1.8.0')
            virtualbox.linked_clone = provider['options']['linked_clone']
          end
        else
          if Gem::Version.new(Vagrant::VERSION) >= Gem::Version.new('1.8.0')
            virtualbox.linked_clone = true
          end
        end

        # Custom
        if provider['options']
          provider['options'].each { |key, value|
            if key != 'memory' && key != 'cpus' && key != 'linked_clone' && key != 'ssh_insert_key' && key != 'synced_folder'
              eval("virtualbox.#{key} = #{value}")
            end
          }
        end

        # Raw Configuration
        if provider['raw_config_args']
          provider['raw_config_args'].each { |raw_config_arg|
            eval("virtualbox.#{raw_config_arg}")
          }
        end
      end

      # The vagrant-vbguest plugin attempts to update packages
      # before a RHEL based VM is registered.
      # TODO: Port from the old .j2, should be done in raw config
      if (vagrant_config['platform'] =~ /rhel/i) != nil
        if Vagrant.has_plugin?('vagrant-vbguest')
          config.vbguest.auto_update = false
        end
      end
    end

    ##
    # VMware (vmware_fusion, vmware_workstation and vmware_desktop)
    ##
    if provider['name'].start_with?('vmware_')
      config.vm.provider provider['name'] do |vmware|
        vmware.vmx['memsize'] = provider['options']['memory']
        vmware.vmx['numvcpus'] = provider['options']['cpus']

        # Custom
        if provider['options']
          provider['options'].each { |key, value|
            if key != 'memory' && key != 'cpus' && key != 'ssh_insert_key' && key != 'synced_folder'
              eval("vmware.#{key} = #{value}")
            end
          }
        end

        # Raw Configuration
        if provider['raw_config_args']
          provider['raw_config_args'].each { |raw_config_arg|
            eval("vmware.#{raw_config_arg}")
          }
        end
      end
    end

    ##
    # Parallels
    ##
    if provider['name'] == 'parallels'
      config.vm.provider provider['name'] do |parallels|
        parallels.memory = provider['options']['memory']
        parallels.cpus = provider['options']['cpus']

        # Custom
        if provider['options']
          provider['options'].each { |key, value|
            if key != 'memory' && key != 'cpus' && key != 'ssh_insert_key' && key != 'synced_folder'
              eval("parallels.#{key} = #{value}")
            end
          }
        end

        # Raw Configuration
        if provider['raw_config_args']
          provider['raw_config_args'].each { |raw_config_arg|
            eval("parallels.#{raw_config_arg}")
          }
        end
      end
    end

    ##
    # Libvirt
    ##
    if provider['name'] == 'libvirt'
      config.vm.provider provider['name'] do |libvirt|
        libvirt.memory = provider['options']['memory']
        libvirt.cpus = provider['options']['cpus']

        # Custom
        if provider['options']
          provider['options'].each { |key, value|
            if key != 'memory' && key != 'cpus' && key != 'ssh_insert_key' && key != 'synced_folder'
              eval("libvirt.#{key} = #{value}")
            end
          }
        end

        # Raw Configuration
        if provider['raw_config_args']
          provider['raw_config_args'].each { |raw_config_arg|
            eval("libvirt.#{raw_config_arg}")
          }
        end
      end
    end
  end

  ##
  # Instances
  ##
  if vagrant_config['instance']
    instance = vagrant_config['instance']
    config.vm.define instance['name'] do |c|
      c.vm.hostname = instance['name']

      if instance['interfaces']
        instance['interfaces'].each { |interface|
          if interface['type'] == 'static'
            c.vm.network "#{interface['network_name']}", type: "#{interface['type']}", auto_config: "#{interface['auto_config']}", ip: "#{interface['ip']}"
          else
            c.vm.network "#{interface['network_name']}", type: "#{interface['type']}", auto_config: "#{interface['auto_config']}"
          end
        }
      end

      if instance['raw_config_args']
        instance['raw_config_args'].each { |raw_config_arg|
          eval("c.#{raw_config_arg}")
        }
      end
    end
  end
end
'''.strip()  # noqa


class VagrantClient(object):
    def __init__(self, module):
        self._module = module

        self._config = self._get_config()
        self._vagrantfile = self._config.driver.vagrantfile
        self._vagrant = self._get_vagrant()
        self._write_configs()

    def up(self):
        changed = False
        cd = self._created()
        if not cd:
            changed = True
            provision = self._module.params['provision']
            for line in self._vagrant.up(provision=provision, stream_output=True):
                # NOTE: Add prefix to ensure that output of 'vagrant up'
                # doesn't start with one of the JSON start characters { or ].
                print('<vagrant_output> {}'.format(line))

        self._module.exit_json(changed=changed, **self._conf())

    def destroy(self):
        changed = False
        cd = self._created()
        if cd:
            changed = True
            if self._module.params['force_stop']:
                self._vagrant.halt(force=True)
            self._vagrant.destroy()

        self._module.exit_json(changed=changed)

    def _conf(self):
        instance_name = self._module.params['instance_name']

        return self._vagrant.conf(vm_name=instance_name)

    def _status(self):
        instance_name = self._module.params['instance_name']
        s = self._vagrant.status(vm_name=instance_name)[0]

        return {'name': s.name, 'state': s.state, 'provider': s.provider}

    def _created(self):
        status = self._status()
        if status['state'] == 'running':
            return status
        return {}

    def _get_config(self):
        molecule_file = os.environ['MOLECULE_FILE']

        return molecule.config.Config(molecule_file)

    def _write_vagrantfile(self):
        template = molecule.util.render_template(
            VAGRANTFILE_TEMPLATE,
            vagrantfile_config=self._config.driver.vagrantfile_config)
        molecule.util.write_file(self._vagrantfile, template)

    def _write_vagrantfile_config(self, data):
        molecule.util.write_file(self._config.driver.vagrantfile_config,
                                 molecule.util.safe_dump(data))

    def _write_configs(self):
        self._write_vagrantfile_config(self._get_vagrant_config_dict())
        self._write_vagrantfile()

    def _get_vagrant(self):
        env = os.environ.copy()
        env['VAGRANT_CWD'] = os.environ['MOLECULE_EPHEMERAL_DIRECTORY']
        v = vagrant.Vagrant(quiet_stdout=False, quiet_stderr=False, env=env)

        return v

    def _get_vagrant_config_dict(self):
        d = {
            'instance': {
                'name': self._module.params['instance_name'],
                'interfaces': self._module.params['instance_interfaces'],
                'raw_config_args':
                self._module.params['instance_raw_config_args'],
            },
            'platform': {
                'box': self._module.params['platform_box'],
                'box_version': self._module.params['platform_box_version'],
                'box_url': self._module.params['platform_box_url'],
            },
            'provider': {
                'name': self._module.params['provider_name'],
                'options': {
                    'memory': self._module.params['provider_memory'],
                    'cpus': self._module.params['provider_cpus'],
                },
                'raw_config_args':
                self._module.params['provider_raw_config_args'],
            }
        }

        # TODO(retr0h): Should we move this to config.merge_dicts()?
        d['provider']['options'].update(
            self._module.params['provider_options'])

        return d


def main():
    module = AnsibleModule(  # noqa
        argument_spec=dict(
            instance_name=dict(type='str', required=True),
            instance_interfaces=dict(type='list', default=[]),
            instance_raw_config_args=dict(type='list', default=None),
            platform_box=dict(type='str', required=True),
            platform_box_version=dict(type='str'),
            platform_box_url=dict(type='str'),
            provider_name=dict(type='str', default='virtualbox'),
            provider_memory=dict(type='int', default=512),
            provider_cpus=dict(type='int', default=2),
            provider_options=dict(type='dict', default={}),
            provider_raw_config_args=dict(type='list', default=None),
            provision=dict(type='bool', default=False),
            force_stop=dict(type='bool', default=False),
            state=dict(type='str', default='up', choices=['up', 'destroy'])),
        supports_check_mode=False)

    v = VagrantClient(module)

    if module.params['state'] == 'up':
        v.up()

    if module.params['state'] == 'destroy':
        v.destroy()


from ansible.module_utils.basic import *  # noqa
main()
