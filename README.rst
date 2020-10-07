****************
My Molecule
****************

.. image:: https://img.shields.io/pypi/v/molecule
   :target: https://pypi.org/project/molecule/
   :alt: PyPI Package

.. image:: https://readthedocs.org/projects/molecule/badge/?version=latest
   :target: https://molecule.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://github.com/ansible-community/molecule/workflows/tox/badge.svg
   :target: https://github.com/ansible-community/molecule/actions

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/python/black
   :alt: Python Black Code Style

.. image:: https://img.shields.io/badge/Code%20of%20Conduct-silver.svg
   :target: https://docs.ansible.com/ansible/latest/community/code_of_conduct.html
   :alt: Ansible Code of Conduct

.. image:: https://img.shields.io/badge/Discussions-silver.svg
   :target: https://github.com/ansible-community/molecule/discussions
   :alt: Discussions

.. image:: https://img.shields.io/badge/license-MIT-brightgreen.svg
   :target: LICENSE
   :alt: Repository License

About Ansible Molecule
======================

Molecule project is designed to aid in the development and testing of
`Ansible`_ roles.

Molecule provides support for testing with multiple instances, operating
systems and distributions, virtualization providers, test frameworks and
testing scenarios.

Molecule encourages an approach that results in consistently developed roles
that are well-written, easily understood and maintained.

Molecule supports only the latest two major versions of Ansible (N/N-1),
meaning that if the latest version is 2.9.x, we will also test our code with
2.8.x.

Once installed, the command line can be called using any of the methods below:

.. code-block:: bash

    molecule ...
    mol ...  # same as above, introduced in 3.0.5
    python3 -m molecule ...  # python module calling method

.. _`Ansible`: https://ansible.com

.. _documentation:

Documentation
=============

Read the documentation and more at https://molecule.readthedocs.io/.

.. _get-involved:

Get Involved
============

* Join us in the ``#ansible-molecule`` channel on `Freenode`_.
* Check github `discussions`_.
* Join the community working group by checking the `wiki`_.
* Want to know about releases, subscribe to `ansible-announce list`_.
* For the full list of Ansible email Lists, IRC channels see the
  `communication page`_.

If you want to get moving fast and make a quick patch:

.. code-block:: bash

    $ git clone https://github.com/ansible-community/molecule && cd molecule
    $ python3 -m venv .venv && source .venv/bin/activate
    $ python3 -m pip install -U setuptools pip tox

And you're ready to make your changes!

.. _`Freenode`: https://freenode.net
.. _`discussions`: https://github.com/ansible-community/molecule/discussions
.. _`wiki`: https://github.com/ansible/community/wiki/Molecule
.. _`ansible-announce list`: https://groups.google.com/group/ansible-announce
.. _`communication page`: https://docs.ansible.com/ansible/latest/community/communication.html

.. _authors:

Authors
=======

Molecule project was created by `Retr0h <https://github.com/retr0h>`_ and it is
now community-maintained as part of the `Ansible`_ by Red Hat project.

.. _license:

License
=======

The `MIT`_ License.

.. _`MIT`: https://github.com/ansible-community/molecule/blob/master/LICENSE

The logo is licensed under the `Creative Commons NoDerivatives 4.0 License`_.

If you have some other use in mind, contact us.

.. _`Creative Commons NoDerivatives 4.0 License`: https://creativecommons.org/licenses/by-nd/4.0/
