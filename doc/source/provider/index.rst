.. _providers:

*********
Providers
*********

Vagrant uses `provider plugins`_ to support managing machines onvarious
virtualization platforms. There are workstation-local provider plugins
such as `VirtualBox`_ and VMware Fusion/Workstation and cloud-based providers
such as AWS/EC2.

Molecule can be configured to give provider-specific configuration data in
`molecule.yml` - in the `vagrant.providers` hash. Necessarily, the configuration
requirements/options are much more complicated for cloud-based providers than they
are for workstation-local virtualization provider plugins.

.. include:: libvirt/index.rst
.. include:: libvirt/usage.rst
.. include:: parallels.rst
.. include:: virtualbox.rst
.. include:: vmware_fusion.rst

.. _`VirtualBox`: http://docs.vagrantup.com/v2/virtualbox/index.html
.. _`provider plugins`: https://www.vagrantup.com/docs/providers/
