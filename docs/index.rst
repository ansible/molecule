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
    python3 -m molecule ...  # python module calling method

.. _`Ansible`: https://ansible.com

Installation and Upgrade
========================

.. toctree::
   :maxdepth: 1

   Installation <installation>

Using Molecule
==============

.. toctree::
   :maxdepth: 1

   Getting Started <getting-started>
   CI/CD Usage <ci>
   Command Line Reference <usage>
   Configuration <configuration>

Common Molecule Use Cases
=========================

.. toctree::
   :maxdepth: 1

   Common Use Cases <examples>
   Frequently Asked Questions <faq>

Contributing to Molecule
========================

.. toctree::
   :maxdepth: 1

   Contributing <contributing>


References and Appendices
=========================

* :ref:`genindex`

External Resources
==================

Below you can see a list of useful articles and presentations, recently updated
being listed first:

- `Ansible Collections: Role Tests with Molecule <https://ericsysmin.com/2020/04/30/ansible-collections-role-tests-with-molecule/>`_ `@ericsysmin`
- `Molecule v3 Slides <https://sbarnea.com/slides/molecule/#/>`_ `@ssbarnea`.
- `Testing your Ansible roles with Molecule <https://www.jeffgeerling.com/blog/2018/testing-your-ansible-roles-molecule>`_ `@geerlinguy`
- `How to test Ansible and don’t go nuts <https://www.goncharov.xyz/it/ansible-testing-en.html>`_ `@ultral`

.. When updating the list remember to remove broken links or outdated content
   that is no longer applicable to current versions. If older articles are
   updated to match latest versions move them up.
