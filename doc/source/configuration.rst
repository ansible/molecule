Configuration
=============

Config
------

.. autoclass:: molecule.config.Config
   :undoc-members:

Variable Substitution
---------------------

.. autoclass:: molecule.interpolation.Interpolator
   :undoc-members:


Dependency
----------

Testing roles may rely upon additional dependencies.  Molecule handles managing
these dependencies by invoking configurable dependency managers.

Ansible Galaxy
^^^^^^^^^^^^^^

.. autoclass:: molecule.dependency.ansible_galaxy.AnsibleGalaxy
   :undoc-members:

Gilt
^^^^

.. autoclass:: molecule.dependency.gilt.Gilt
   :undoc-members:

Driver
------

Molecule uses `Ansible`_ to manage instances to operate on.  Molecule supports
any provider `Ansible`_ supports.  This work is offloaded to the `provisioner`.

.. important::

    The verifier must support the Ansible provider for proper Molecule
    integration.

    The driver's python package requires installation.

.. _`Ansible`: https://docs.ansible.com


Docker
^^^^^^

.. autoclass:: molecule.driver.dockr.Dockr
   :undoc-members:

Lint
----

Molecule handles role linting by invoking configurable linters.

Ansible Lint
^^^^^^^^^^^^

.. autoclass:: molecule.lint.ansible_lint.AnsibleLint
   :undoc-members:


Platforms
---------

.. autoclass:: molecule.platforms.Platforms
   :undoc-members:

Provisioner
-----------

Molecule handles provisioning and converging the role.

Ansible
^^^^^^^

.. autoclass:: molecule.provisioner.ansible.Ansible
   :undoc-members:

Scenario
--------

Molecule treats scenarios as a first-class citizens, with a top-level
configuration syntax.

.. autoclass:: molecule.scenario.Scenario
   :undoc-members:

Verifier
--------

Molecule handles role testing by invoking configurable verifiers.

Testinfra
^^^^^^^^^

.. autoclass:: molecule.verifier.flake8.Flake8
   :undoc-members:

.. autoclass:: molecule.verifier.testinfra.Testinfra
   :undoc-members:
