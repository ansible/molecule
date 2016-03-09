Providers
=========

Vagrant uses `provider plugins`_ to support managing machines on various virtualization platforms. There are workstation-local provider plugins such as `VirtualBox`_ and VMware Fusion/Workstation and cloud-based providers such as OpenStack and AWS/EC2.

Molecule can be configured to give provider-specific configuration data in `molecule.yml` - in the `vagrant.providers` hash. Necessarily, the configuration requirements/options are much more complicated for cloud-based providers than they are for workstation-local virtualization provider plugins.

OpenStack
---------

Molecule is known to work with the `vagrant-openstack-provider`_ provider plugin, which you can install with::

      $ vagrant plugin install vagrant-openstack-provider

.. _`provider plugins`: http://docs.vagrantup.com/v2/providers/index.html
.. _`vagrant-openstack-provider`: https://github.com/ggiamarchi/vagrant-openstack-provider

Commonly, the OpenStack CLI clients are configured using a simple shell script that can be downloaded from Horizon, the OpenStack web interface, `<tenant_name>-openrc.sh`, and which sets a few environment variables to get you going. Molecule makes the assumption that these environment variables are set to get its default behaviour, but these settings can be overridden.

Molecule will generate a Vagrantfile which will default to using these environment variables to set the configuration for `configuration for vagrant-openstack-provider`_:

Credentials
^^^^^^^^^^^

=================================   ======================
vagrant-openstack-provider option   molecule default value
=================================   ======================
openstack_auth_url                  ENV['OS_AUTH_URL']
username                            ENV['OS_USERNAME']
password                            ENV['OS_PASSWORD']
tenant_name                         ENV['OS_TENANT_NAME']
region                              ENV['OS_REGION_NAME']
=================================   ======================

Endpoints
^^^^^^^^^

Different OpenStack distributions often use different endpoints for the various services; if you do not specify any of these to Molecule, vagrant-openstack-provider will try to get them from the catalog endpoint. For completeness, the example shows how to specify them to Molecule so that they get to the provider plugin.

If the defaults are not working for you and you're not sure what to specify, you can discover your OpenStack's endpoints using the command-line clients:

* `nova endpoints` if you are using `python-novaclient`_
* `openstack endpoint list`, followed by `openstack endpoint show <service_type>` if you are using the newer `python-openstackclient`_

Networks
^^^^^^^^

You can specify a list of `Networks`_ which should defined as the YAML description of the data structure described.

Volumes
^^^^^^^

You can specify a list of `Volumes`_ which should defined as the YAML description of the data structure described.
If you want to boot from a volume, instead of an image, specify the volume id in the `volume_boot` key of the provider's platform list.

Stacks
^^^^^^

You can specify a list of `Stacks`_ which should defined as the YAML description of the data structure described.

Simple Example
^^^^^^^^^^^^^^

.. code-block:: yaml

      ---
      ansible:
        playbook: playbook.yml
        sudo: True
        verbose: vvvv

      vagrant:
        raw_config_args:
          - "ssh.insert_key = false"

        platforms:
          - name: ubuntu
            box: ubuntu/trusty32

        providers:
          - name: virtualbox
            type: virtualbox
            options:
              memory: 512
          - name: openstack
            type: openstack
            box: os_dummy
            flavor: m1.small
            platforms:
              - name: ubuntu
                image: ubuntu-14.04-server-cloudimg

Comprehensive Example
^^^^^^^^^^^^^^^^^^^^^

This example is far more extensive than you likely need and it demonstrates lots of options that you probably don't want to set.

.. code-block:: yaml

      ---
      ansible:
        playbook: playbook.yml
        sudo: True
        sudo_user: False
        verbose: vvvv

      vagrant:
        raw_config_args:
          - "ssh.insert_key = false"

        platforms:
          - name: ubuntu
            box: ubuntu/precise32
          - name: trusty64
            box: trusty64
            box_version: "~> 20151130.0.0"
            box_url: https://vagrantcloud.com/ubuntu/boxes/trusty64/versions/14.04/providers/virtualbox.box
          - name: rhel-7
            box: rhel/rhel-7
            triggers:
              - trigger: before
                action: destroy
                cmd: run_remote 'subscription-manager unregister'

        providers:
          - name: virtualbox
            type: virtualbox
            options:
              memory: 512
          - name: openstack
            type: openstack
            username: myname
            password: 'something'
            region: 'RegionOne'
            tenant_name: 'myproject'
            keypair_name: 'mykey'
            private_key_path: "ENV['HOME'] + '/.ssh/id_rsa'"
            box: 'os_dummy'
            flavor: 'm1.small'
            raw_options:
              server_create_timeout: 120
              server_active_timeout: 120
              server_stop_timeout: 60
            endpoints:
              auth_url: 'http://api-cntrl1.os.example.com:5000/v2.0'
              compute_url: 'http://api.cntrl1.mc.metacloud.in:8774/v2'
              image_url: 'http://api-cntrl1.os.example.com:9292/v1'
              network_url: 'http://api-cntrl1.os.example.com:8774/v2'
              volume_url: 'http://api.cntrl1.os.example.com:8776/v1'
            networks:
              - 'mynet1'
              - { name: 'mynet2', address: '192.168.32.3' }
              - { id: 'ab5cc992-95fa-454d-91c1-5d06ed16c2f5', address: '192.168.32.4' }
            security_groups:
              - 'default'
              - 'http'
            platforms:
              - name: ubuntu
                image: 'ubuntu-14.04'
                username: ubuntu
              - name: rhel-7
                volume_boot: '5f580a79-ca75-470e-a956-8b4b3b2ddbb8'
                username: cloud

Other Notes
^^^^^^^^^^^

* `private_key_path`, as with several other values, can be any valid Ruby because it will appear in the Vagrantfile that molecule will generate.

* `box_version`, defaults to '=', can include an constraints like '<, >, >=, <=, ~.' as listed in the `Versioning`_ docs.

* `triggers` enables very basic support for the vagrant-triggers plugin. During `molecule create`, if the plugin is not found it will be automatically installed.

..  _`configuration for vagrant-openstack-provider`: https://github.com/ggiamarchi/vagrant-openstack-provider/blob/master/README.md#configuration
.. _`VirtualBox`: http://docs.vagrantup.com/v2/virtualbox/index.html
.. _`python-novaclient`: http://pypi.python.org/pypi/python-novaclient
.. _`python-openstackclient`: http://pypi.python.org/pypi/python-openstackclient
.. _`Networks`: https://github.com/ggiamarchi/vagrant-openstack-provider/blob/master/README.md#networks
.. _`Volumes`: https://github.com/ggiamarchi/vagrant-openstack-provider/blob/master/README.md#volumes
.. _`Stacks`: https://github.com/ggiamarchi/vagrant-openstack-provider/blob/master/README.md#orchestration-stacks
.. _`Versioning`: https://docs.vagrantup.com/v2/boxes/versioning.html

Libvirt
---------

The libvirt toolkit is known to work with the `vagrant-libvirt`_ provider plugin. But before installing this plugin you need to have libvirt installed(if you plan to run the tests on your local machine). Some users have reported dependency issues while installing vagrant-libvirt, so it is highly recommended to check `this section`_. You also need a vagrant compatible version installed on your machine(note that, not all versions are supported. Check the vagrant-libvirt documentation).


You can install the vagrant-libvirt plugin with::

      $ vagrant plugin install vagrant-libvirt

.. _`vagrant-libvirt`: https://github.com/pradels/vagrant-libvirt


.. _`this section`: https://github.com/pradels/vagrant-libvirt#possible-problems-with-plugin-installation-on-linux

Molecule allows to specify `provider options`_ and `domain specific options`_  within the molecule.yml file, in the providers section.

.. _`domain specific options`: https://github.com/pradels/vagrant-libvirt#domain-specific-options

Provider options
^^^^^^^^^^^^^^^^
These options are described in the `provider options`_ section of the vagrant-libvirt project site:

Although it should work without any configuration for most people, this provider exposes quite a few provider-specific configuration options. The following options allow you to configure how vagrant-libvirt connects to libvirt, and are used to generate the `libvirt connection URI`_:

* `driver` - A hypervisor name to access. For now only kvm and qemu are supported.
* `host` - The name of the server, where libvirtd is running. You want to use this option when creating the VM in a remote host.
* `connect_via_ssh` - If use ssh tunnel to connect to Libvirt. Absolutely needed to access libvirt on remote host. It will not be able to get the IP address of a started VM otherwise.
* `username` - Username and password to access Libvirt.
* `password` - Password to access Libvirt.
* `id_ssh_key_file` - If not nil, uses this ssh private key to access Libvirt. Default is $HOME/.ssh/id_rsa. Prepends $HOME/.ssh/ if no directory.
* `socket` - Path to the libvirt unix socket (eg: /var/run/libvirt/libvirt-sock)
* `uri` - For advanced usage. Directly specifies what libvirt connection URI vagrant-libvirt should use. Overrides all other connection configuration options.

Connection-independent options:

* `storage_pool_name` - Libvirt storage pool name, where box image and instance snapshots will be stored.

.. _`provider options`: https://github.com/pradels/vagrant-libvirt#provider-options
.. _`libvirt connection URI`: http://libvirt.org/uri.html

Here is an example of how could look like your molecule.yml file:

.. code-block:: yaml

Domain Specific Options
^^^^^^^^^^^^^^^^^^^^^^^

* `disk_bus` - The type of `disk device`_ to emulate. Defaults to virtio if not set.
* `nic_model_type` - parameter specifies the model of the network adapter when you create a domain value by default virtio KVM believe possible values, see the `nics documentation`_.
* `memory` - Amount of memory in MBytes. Defaults to 512 if not set.
* `cpus` - Number of virtual cpus. Defaults to 2 if not set.
* `nested` - `Enable nested virtualization`_. Default is false.
* `cpu_mode` - `CPU emulation mode`_. Defaults to 'host-model' if not set. Allowed values: host-model, host-passthrough.
* `Other options` - Such as graphics_port, suspend_mode, boot, etc. Please, take a look at the `vagrant-libvirt`_ documentation for seeing all available options.

.. _`disk device`: http://libvirt.org/formatdomain.html#elementsDisks
.. _`nics documentation`: https://libvirt.org/formatdomain.html#elementsNICSModel
.. _`Enable nested virtualization`: https://github.com/torvalds/linux/blob/master/Documentation/virtual/kvm/nested-vmx.txt
.. _`CPU emulation mode`: https://libvirt.org/formatdomain.html#elementsCPU

Usage
^^^^^

All libvirt specific options(such as the one above, provider specific and domain options) must be specified in the providers section. Nevertheless, other options such as synced or network settings should be added to the raw_config_args, as they are vagrant generic parameters. Note that you can use special libvirt parameters such as "libvirt__tunnel_type", as it is shown in the example below.

Please, refer to the `vagrant-libvirt`_ documentation for getting a better understanding of all available options.

There is an example:

.. code-block:: yaml

	---
	vagrant:

	  platforms:
	    - name: rhel6
	      box: rhel/rhel-6
	    - name: rhel7
	      box: rhel/rhel-7
	    - name: centos7
	      box: centos/7

	  providers:
	    - name: libvirt
	      type: libvirt
	      options:
		memory: 1024
		cpus: 2
		driver: kvm #Note that the two available drivers are kvm and qemu(refer to the vagrant-libvirt doc).
		video_type: vga

	  instances:
	    - name: ansible-role
	      raw_config_args:
		- "ssh.pty = true"
		- "vm.synced_folder './', '/vagrant', disabled: true"
		- "vm.network :private_network, :libvirt__dhcp_enabled=> false ,:libvirt__tunnel_type => 'server', :libvirt__tunnel_port => '11111'"
	      options:
		append_platform_to_hostname: no

	      ansible_groups:
		- group_1

