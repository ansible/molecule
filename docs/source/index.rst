Molecule
========

Molecule is designed to aid in the development and testing of
`Ansible`_ roles including support for multiple instances, distributions, platforms and test frameworks.

It leverages `Vagrant`_ to manage virtual machines,
with support for multiple Vagrant providers (currently VirtualBox and OpenStack)
and `Serverspec`_ or `Testinfra`_ to run tests.  Molecule uses an `Ansible`_
`playbook`_ (``playbook.yml``), to execute the `role`_ and its tests.

Some of the UI was inspired by `Test Kitchen`_.


Contents:

.. toctree::
   :maxdepth: 3

   usage

.. _`Ansible`: https://docs.ansible.com
.. _`Vagrant`: http://docs.vagrantup.com/v2
.. _`Test Kitchen`: http://kitchen.ci
.. _`playbook`: https://docs.ansible.com/ansible/playbooks.html
.. _`role`: http://docs.ansible.com/ansible/playbooks_roles.html
.. _`Serverspec`: http://serverspec.org
.. _`Testinfra`: http://testinfra.readthedocs.org

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
