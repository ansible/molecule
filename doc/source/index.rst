Molecule
========

Molecule is designed to aid in the development and testing of
`Ansible`_ roles including support for multiple instances,
operating system distributions, virtualization providers and test frameworks.

It leverages `Vagrant`_, `Docker`_, `OpenStack`_, and `libvirt`_ to manage
virtual machines/containers, with support for multiple Vagrant providers
(currently VirtualBox, Parallels and VMware Fusion).  Molecule supports
`Serverspec`_ or `Testinfra`_ to run tests.  Molecule uses an `Ansible`_
`playbook`_ (``playbook.yml``), to execute the `role`_ and its tests.

Some of the UI was inspired by `Test Kitchen`_.

Contents:

.. toctree::
   :maxdepth: 3

   usage
   providers
   drivers
   development

.. _`Ansible`: https://docs.ansible.com
.. _`Test Kitchen`: http://kitchen.ci
.. _`playbook`: https://docs.ansible.com/ansible/playbooks.html
.. _`role`: http://docs.ansible.com/ansible/playbooks_roles.html
.. _`Serverspec`: http://serverspec.org
.. _`Testinfra`: http://testinfra.readthedocs.org
.. _`Vagrant`: http://docs.vagrantup.com/v2
.. _`Docker`: https://www.docker.com
.. _`OpenStack`: https://www.openstack.org
.. _`libvirt`: http://libvirt.org

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
