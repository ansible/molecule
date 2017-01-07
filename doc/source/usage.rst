Usage
=====

Quick Start
^^^^^^^^^^^

Install Molecule using pip:

.. code-block:: bash

  $ pip install molecule --pre

Install dependencies using pip:

.. code-block:: bash

  $ pip install ansible
  $ pip install docker-py

Create a new role:

.. code-block:: bash

  $ molecule init role --role-name foo
  --> Initializing new role foo...
  Successfully initialized role in /private/tmp/foo.

Or Create a new scenario in an existing role:

.. code-block:: bash

  $ cd foo
  $ molecule init scenario --scenario-name default --role-name foo
  --> Initializing new scenario default...
  Successfully initialized scenario in /tmp/foo/molecule/default.

Update the role with needed functionality and tests.  Now test it:

.. code-block:: bash

  $ cd foo
  $ molecule test
  ...

Converge
^^^^^^^^

Converge will execute the sequences necessary to converge the instances.

.. autoclass:: molecule.command.converge.Converge
   :undoc-members:
   :members: execute

Create
^^^^^^

.. autoclass:: molecule.command.create.Create
   :undoc-members:
   :members: execute

Dependency
^^^^^^^^^^

.. autoclass:: molecule.command.dependency.Dependency
   :undoc-members:
   :members: execute

Destroy
^^^^^^^

.. autoclass:: molecule.command.destroy.Destroy
   :undoc-members:
   :members: execute

Idempotence
^^^^^^^^^^^

.. autoclass:: molecule.command.idempotence.Idempotence
   :undoc-members:
   :members: execute

Init
^^^^

Initialize a new role:

.. automethod:: molecule.command.init._init_new_role

Initialize a new scenario:

.. automethod:: molecule.command.init._init_new_scenario

Lint
^^^^

.. autoclass:: molecule.command.lint.Lint
   :undoc-members:
   :members: execute

Syntax
^^^^^^

.. autoclass:: molecule.command.syntax.Syntax
   :undoc-members:
   :members: execute

Test
^^^^

Test will execute the sequences necessary to test the instances.

.. autoclass:: molecule.command.test.Test
   :undoc-members:
   :members: execute

Verify
^^^^^^

.. autoclass:: molecule.command.verify.Verify
   :undoc-members:
   :members: execute

