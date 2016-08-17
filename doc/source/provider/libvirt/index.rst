Libvirt
=======

The libvirt toolkit is known to work with the `vagrant-libvirt`_ provider
plugin. But before installing this plugin you need to have libvirt installed
(if you plan to run the tests on your local machine). Some users have reported
dependency issues while installing vagrant-libvirt, so it is highly recommended
to check `this section`_.  You also need a vagrant compatible version installed
on your machine (note that, not all versions are supported.  Check the
vagrant-libvirt documentation).

You can install the vagrant-libvirt plugin with::

    $ vagrant plugin install vagrant-libvirt

.. _`vagrant-libvirt`: https://github.com/pradels/vagrant-libvirt
.. _`this section`: https://github.com/pradels/vagrant-libvirt#possible-problems-with-plugin-installation-on-linux

Molecule allows to specify `provider options`_ and `domain specific options`_
within the molecule.yml file, in the providers section.

.. _`provider options`: https://github.com/pradels/vagrant-libvirt#provider-options
.. _`domain specific options`: https://github.com/pradels/vagrant-libvirt#domain-specific-options

Options
-------

These options are described in the `provider options`_ section of the
vagrant-libvirt project site:

Although it should work without any configuration for most people, this
provider exposes quite a few provider-specific configuration options. The
following options allow you to configure how vagrant-libvirt connects to
libvirt, and are used to generate the `libvirt connection URI`_:

* ``driver`` - A hypervisor name to access. For now only kvm and qemu are
  supported.
* ``host`` - The name of the server, where libvirtd is running. You want to use
  this option when creating the VM in a remote host.
* ``connect_via_ssh`` - If use ssh tunnel to connect to Libvirt. Absolutely
  needed to access libvirt on remote host. It will not be able to get the IP
  address of a started VM otherwise.
* ``username`` - Username and password to access Libvirt.
* ``password`` - Password to access Libvirt.
* ``id_ssh_key_file`` - If not nil, uses this ssh private key to access
  Libvirt. Default is $HOME/.ssh/id_rsa. Prepends $HOME/.ssh/ if no directory.
* ``socket`` - Path to the libvirt unix socket
* ``uri`` - For advanced usage.  Directly specifies what libvirt connection URI
  vagrant-libvirt should use. Overrides all other connection configuration
  options.

Connection-independent options:

* ``storage_pool_name`` - Libvirt storage pool name, where box image and
  instance snapshots will be stored.

.. _`provider options`: https://github.com/pradels/vagrant-libvirt#provider-options
.. _`libvirt connection URI`: http://libvirt.org/uri.html

Domain Specific Options
-----------------------

* ``disk_bus`` - The type of `disk device`_ to emulate. Defaults to virtio if
  not set.
* ``nic_model_type`` - parameter specifies the model of the network adapter
  when you create a domain value by default virtio KVM believe possible values,
  see the `nics documentation`_.
* ``memory`` - Amount of memory in MBytes. Defaults to 512 if not set.
* ``cpus`` - Number of virtual cpus. Defaults to 2 if not set.
* ``nested`` - `Enable nested virtualization`_. Default is false.
* ``cpu_mode`` - `CPU emulation mode`_. Defaults to 'host-model' if not set.
  Allowed values: host-model, host-passthrough.
* ``Other options`` - Such as graphics_port, suspend_mode, boot, etc. Please,
  take a look at the `vagrant-libvirt`_ documentation for seeing all available
  options.

.. _`disk device`: http://libvirt.org/formatdomain.html#elementsDisks
.. _`nics documentation`: https://libvirt.org/formatdomain.html#elementsNICSModel
.. _`Enable nested virtualization`: https://github.com/torvalds/linux/blob/master/Documentation/virtual/kvm/nested-vmx.txt
.. _`CPU emulation mode`: https://libvirt.org/formatdomain.html#elementsCPU
