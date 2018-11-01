********
Molecule
********

.. image:: https://badge.fury.io/py/molecule.svg
   :target: https://badge.fury.io/py/molecule
   :alt: PyPI Package

.. image:: https://readthedocs.org/projects/molecule/badge/?version=latest
   :target: https://molecule.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/Code%20of%20Conduct-Ansible-silver.svg
   :target: https://docs.ansible.com/ansible/latest/community/code_of_conduct.html
   :alt: Ansible Code of Conduct

.. image:: https://img.shields.io/badge/Mailing%20lists-Ansible-orange.svg
   :target: https://docs.ansible.com/ansible/latest/community/communication.html#mailing-list-information
   :alt: Ansible mailing lists

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

.. _`playbooks`: https://docs.ansible.com/ansible/latest/playbooks.html
.. _`role`: http://docs.ansible.com/ansible/latest/playbooks_roles.html

Quick Start
===========

Installing
----------

.. image:: https://asciinema.org/a/161970.png
   :target: https://asciinema.org/a/161970?speed=5&autoplay=1&loop=1
   :alt: Installing

Creating a new role
-------------------

.. image:: https://asciinema.org/a/161976.png
   :target: https://asciinema.org/a/161976?speed=5&autoplay=1&loop=1
   :alt: Creating a new role

Testing a new role
-------------------

.. image:: https://asciinema.org/a/161977.png
   :target: https://asciinema.org/a/161977?speed=5&autoplay=1&loop=1
   :alt: Testing a new role

Testing an existing role
------------------------

.. image:: https://asciinema.org/a/AkQ4KhxuGAxwn1YJX3tM5BZld.png
   :target: https://asciinema.org/a/AkQ4KhxuGAxwn1YJX3tM5BZld?speed=5&autoplay=1&loop=1
   :alt: Testing an existing role

Docker in Docker
----------------

.. image:: https://asciinema.org/a/172713.png
   :target: https://asciinema.org/a/172713?speed=5&autoplay=1&loop=1
   :alt: Testing an existing role

Documentation
=============

https://molecule.readthedocs.io/

Contact
=======

* Join us in the ``#ansible-molecule`` channel on `freenode`_.
* Join the discussion in `molecule-users Forum`_
* Want to know about releases, subscribe to `ansible-announce list`_
* For the full list of Ansible email Lists, IRC channels see the `communication page`_

.. _`freenode`: https://freenode.net
.. _`molecule-users Forum`: https://groups.google.com/forum/#!forum/molecule-users
.. _`ansible-announce list`: https://groups.google.com/group/ansible-announce
.. _`communication page`: https://docs.ansible.com/ansible/latest/community/communication.html

Ansible Support
===============

Molecule requires Ansible version 2.4 or later.


License
=======

`MIT`_

.. _`MIT`: https://github.com/ansible/molecule/blob/master/LICENSE

The logo is licensed under the `Creative Commons NoDerivatives 4.0 License`_.
If you have some other use in mind, contact us.

.. _`Creative Commons NoDerivatives 4.0 License`: https://creativecommons.org/licenses/by-nd/4.0/


Authors
=======

Molecule was created by `Retr0h <https://github.com/retr0h>`_ and is now maintained as part of the `Ansible`_ by Red Hat project.

.. _`Ansible`: https://ansible.com
