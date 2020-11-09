Configuration
=============

.. autoclass:: molecule.config.Config()
   :undoc-members:

.. _variable substitution:

Variable Substitution
---------------------

.. autoclass:: molecule.interpolation.Interpolator()
   :undoc-members:

There are following environment variables available in ``molecule.yml``:

================================  ===========================================================
  Variable                          Description
================================  ===========================================================
MOLECULE_DEBUG                    If debug is turned on or off
MOLECULE_FILE                     Path to molecule config file
MOLECULE_ENV_FILE                 Path to molecule environment file
MOLECULE_STATE_FILE               ?
MOLECULE_INVENTORY_FILE           Path to generated inventory file
MOLECULE_EPHEMERAL_DIRECTORY      Path to generated directory, usually
                                  ``~/.cache/molecule/<scenario-name>``
MOLECULE_SCENARIO_DIRECTORY       Path to scenario directory
MOLECULE_PROJECT_DIRECTORY        Path to your project directory
MOLECULE_INSTANCE_CONFIG          ?
MOLECULE_DEPENDENCY_NAME          Dependency type name, usually 'galaxy'
MOLECULE_DRIVER_NAME              Name of the molecule scenario driver
MOLECULE_PROVISIONER_NAME         Name of the provisioner tool (usually 'ansible')
MOLECULE_REPORT                   Name of HTML file where to dump execution report.
MOLECULE_SCENARIO_NAME            Name of the scenario
MOLECULE_VERBOSITY                Determine Ansible verbosity level.
MOLECULE_VERIFIER_NAME            Name of the verifier tool (usually 'ansible')
MOLECULE_VERIFIER_TEST_DIRECTORY  ?
================================  ===========================================================

.. _dependency:

Dependency
----------

Testing roles may rely upon additional dependencies.  Molecule handles managing
these dependencies by invoking configurable dependency managers.

Ansible Galaxy
^^^^^^^^^^^^^^

.. autoclass:: molecule.dependency.ansible_galaxy.AnsibleGalaxy()
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

.. _lint:

Lint
----

Starting with v3, Molecule handles project linting by invoking and external
lint commands as exemplified below.

The decision to remove the complex linting support was not easily taken as we
do find it very useful. The issue was that molecule runs on scenarios and
linting is usually performed at repository level.

It makes little sense to perform linting in more than one place per project.
Molecule was able to use up to three linters and while it was aimed to flexible
about them, it ended up creating more confusions to the users. We decided to
maximize flexibility by just calling an external shell command.

.. code-block:: yaml

    lint: |
      set -e
      yamllint .
      ansible-lint
      flake8

The older format is no longer supported and you have to update the
``molecule.yml`` when you upgrade. If you don't want to do any linting,
it will be enough to remove all lint related sections from the file.

.. code-block:: yaml

    # old v2 format, no longer supported
    lint:
      name: yamllint
      enabled: true
    provisioner:
      lint:
        name: ansible-lint
      options: ...
      env: ...
    verifier:
      lint:
        name: flake8


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
