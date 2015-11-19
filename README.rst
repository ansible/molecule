.. image:: https://cloud.githubusercontent.com/assets/9895/11258895/12a1bb40-8e12-11e5-9adf-9a7aea1ddda9.png
   :alt: Molecule
   :width: 500
   :height: 132
   :align: center

Molecule
========

Molecule is designed to aid in the development and testing of
`Ansible`_ roles including support for multiple instances, 
operating system distributions, virtualization providers and test frameworks.

It leverages `Vagrant`_ to manage virtual machines,
with support for multiple Vagrant providers (currently VirtualBox and OpenStack).
Molecule supports `Serverspec`_ or `Testinfra`_ to run tests.  Molecule uses an `Ansible`_
`playbook`_ (``playbook.yml``), to execute the `role`_ and its tests.

.. _`Ansible`: https://docs.ansible.com
.. _`Vagrant`: http://docs.vagrantup.com/v2
.. _`Test Kitchen`: http://kitchen.ci
.. _`playbook`: https://docs.ansible.com/ansible/playbooks.html
.. _`role`: http://docs.ansible.com/ansible/playbooks_roles.html
.. _`Serverspec`: http://serverspec.org
.. _`Testinfra`: http://testinfra.readthedocs.org

Documentation
-------------

The documentation is built with ``Sphinx`` and uses the ``bootswatch``
theme ``flatly``.

.. code-block:: bash

  $ tox -e docs

License
-------

MIT

The logo is licensed under the `Creative Commons NoDerivatives 4.0 License`_.  If you have some other use in mind, contact us.

.. _`Creative Commons NoDerivatives 4.0 License`: https://creativecommons.org/licenses/by-nd/4.0/
