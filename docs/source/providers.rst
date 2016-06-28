.. _providers:

Providers
=========

Vagrant uses `provider plugins`_ to support managing machines on various virtualization platforms. There are workstation-local provider plugins such as `VirtualBox`_ and VMware Fusion/Workstation and cloud-based providers such as AWS/EC2.

Molecule can be configured to give provider-specific configuration data in `molecule.yml` - in the `vagrant.providers` hash. Necessarily, the configuration requirements/options are much more complicated for cloud-based providers than they are for workstation-local virtualization provider plugins.

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

Other Notes
^^^^^^^^^^^

* `box_version`, defaults to '=', can include an constraints like '<, >, >=, <=, ~.' as listed in the `Versioning`_ docs.

* `triggers` enables very basic support for the vagrant-triggers plugin. During `molecule create`, if the plugin is not found it will be automatically installed.

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
        raw_config_args:
          - "ssh.pty = true"
          - "vm.network :private_network, :libvirt__dhcp_enabled=> false ,:libvirt__tunnel_type => 'server', :libvirt__tunnel_port => '11111'"

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
              driver: kvm #Note that the two available drivers are kvm and qemu (refer to the vagrant-libvirt doc).
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

.. _`VirtualBox`: http://docs.vagrantup.com/v2/virtualbox/index.html
.. _`Versioning`: https://docs.vagrantup.com/v2/boxes/versioning.html
.. _`provider plugins`: https://www.vagrantup.com/docs/providers/
