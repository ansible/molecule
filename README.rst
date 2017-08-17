********
Molecule
********

.. image:: https://badge.fury.io/py/molecule.svg
   :target: https://badge.fury.io/py/molecule
   :alt: PyPI Package

.. image:: https://readthedocs.org/projects/molecule/badge/?version=latest
   :target: https://molecule.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-MIT-brightgreen.svg
   :target: LICENSE
   :alt: Repository License

Molecule is designed to aid in the development and testing of `Ansible`_ roles.
Molecule provides support for testing with multiple instances, operating
systems and distributions, virtualization providers, test frameworks and
testing scenarios.  Molecule is opinionated in order to encourage an approach
that results in consistently developed roles that are well-written, easily
understood and maintained.

Molecule uses `Ansible`_ `playbooks`_ to exercise the `role`_ and its
associated tests.  Molecule supports any provider [#]_ that `Ansible`_
supports.

.. [#]

   Providers can be bare-metal, virtual, cloud or containers.  If Ansible can
   use it, Molecule can test it.  Molecule simply leverages Ansible's module
   system to manage instances.

.. _`playbooks`: https://docs.ansible.com/ansible/playbooks.html
.. _`role`: http://docs.ansible.com/ansible/playbooks_roles.html

Documentation
=============

* `Current Release`_
* `Upcoming Release`_ (preferred)

.. _`Current Release`: https://molecule.readthedocs.io/en/v1/
.. _`Upcoming Release`: https://molecule.readthedocs.io/

Contact
=======

IRC
---

Join us in the #molecule-users channel on `freenode`_.

.. _`freenode`: https://freenode.net

Forums
------

* `molecule-users`_
* `molecule-dev`_

.. _`molecule-users`: https://groups.google.com/forum/#!forum/molecule-users
.. _`molecule-dev`: https://freenode.ne://groups.google.com/forum/#!forum/molecule-dev


Ansible Support
===============

* 2.2.3.0
* 2.3.1.0

.. _`Ansible`: https://docs.ansible.com

License
=======

`MIT`_

.. _`MIT`: https://github.com/metacloud/molecule/blob/master/LICENSE

The logo is licensed under the `Creative Commons NoDerivatives 4.0 License`_.
If you have some other use in mind, contact us.

.. _`Creative Commons NoDerivatives 4.0 License`: https://creativecommons.org/licenses/by-nd/4.0/
