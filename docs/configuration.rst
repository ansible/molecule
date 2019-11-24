Configuration
=============

.. autoclass:: molecule.config.Config()
   :undoc-members:

.. _variable substitution:

Variable Substitution
---------------------

.. autoclass:: molecule.interpolation.Interpolator()
   :undoc-members:

.. _dependency:

Dependency
----------

Testing roles may rely upon additional dependencies.  Molecule handles managing
these dependencies by invoking configurable dependency managers.

Ansible Galaxy
^^^^^^^^^^^^^^

.. autoclass:: molecule.dependency.ansible_galaxy.AnsibleGalaxy()
   :undoc-members:

Gilt
^^^^

.. autoclass:: molecule.dependency.gilt.Gilt()
   :undoc-members:

Shell
^^^^^

.. autoclass:: molecule.dependency.shell.Shell()
   :undoc-members:

.. _driver:

Driver
------

Molecule uses `Ansible`_ to manage instances to operate on.  Molecule supports
any provider `Ansible`_ supports.  This work is offloaded to the `provisioner`.

The driver's name is specified in `molecule.yml`, and can be overridden on the
command line.  Molecule will remember the last successful driver used, and

continue to use the driver for all subsequent subcommands, or until the
instances are destroyed by Molecule.

.. important::

    The verifier must support the Ansible provider for proper Molecule
    integration.

    The driver's python package requires installation.

.. _`Ansible`: https://docs.ansible.com


Delegated
^^^^^^^^^

.. autoclass:: molecule.driver.delegated.Delegated()
   :undoc-members:


Docker
^^^^^^

.. autoclass:: molecule.driver.docker.Docker()
   :undoc-members:


Podman
^^^^^^

.. autoclass:: molecule.driver.podman.Podman()
    :undoc-members:


.. _linters:

Lint
----

Molecule can call multiple external linters by invoking a configurable
shell command. This gets translated into a simple Ansible shell task.

The entire lint section is optional but this does not mean it disabled by
default.

.. code-block:: yaml

    lint:
      cmd: yamllint .
      enabled: true
      env: {}

.. _platforms:

Platforms
---------

.. autoclass:: molecule.platforms.Platforms()
   :undoc-members:

.. _provisioner:

Provisioner
-----------

Molecule handles provisioning and converging the role.

Ansible
^^^^^^^

.. autoclass:: molecule.provisioner.ansible.Ansible()
   :undoc-members:

Lint
....

Molecule handles linting by invoking external executables.

.. _root_scenario:

Scenario
--------

Molecule treats scenarios as a first-class citizens, with a top-level
configuration syntax.

.. autoclass:: molecule.scenario.Scenario()
   :undoc-members:

State
-----

An internal bookkeeping mechanism.

.. autoclass:: molecule.state.State()
  :undoc-members:

.. _verifier:

Verifier
--------

Molecule handles role testing by invoking configurable verifiers.

Ansible
^^^^^^^

.. autoclass:: molecule.verifier.ansible.Ansible()
   :undoc-members:

Testinfra
^^^^^^^^^

.. autoclass:: molecule.verifier.testinfra.Testinfra()
   :undoc-members:
