*******
Drivers
*******

Molecule uses drivers to bring up Ansible ready hosts to operate on.
Currently, Molecule supports three drivers: Vagrant, Docker, and OpenStack.

The driver can set when using ``init`` command or through the
``molecule.yml`` file.

.. include:: docker/index.rst
.. include:: docker/usage.rst

.. include:: openstack/index.rst
.. include:: openstack/usage.rst

.. include:: vagrant/index.rst
.. include:: vagrant/usage.rst
