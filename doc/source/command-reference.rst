.. _command-reference:

Command Reference
=================

.. _check:

Check
^^^^^

.. autoclass:: molecule.command.check.Check()
   :undoc-members:

.. _converge:

Converge
^^^^^^^^

Converge will execute the sequence necessary to converge the instances.

.. autoclass:: molecule.command.converge.Converge()
   :undoc-members:

.. _create:

Create
^^^^^^

.. autoclass:: molecule.command.create.Create()
   :undoc-members:

.. _dependency:

Dependency
^^^^^^^^^^

.. autoclass:: molecule.command.dependency.Dependency()
   :undoc-members:

.. _destroy:

Destroy
^^^^^^^

.. autoclass:: molecule.command.destroy.Destroy()
   :undoc-members:

.. _idempotence:

Idempotence
^^^^^^^^^^^

.. autoclass:: molecule.command.idempotence.Idempotence()
   :undoc-members:

.. _init:

Init
^^^^

.. autoclass:: molecule.command.init.role.Role()
   :undoc-members:

.. autoclass:: molecule.command.init.scenario.Scenario()
   :undoc-members:

.. autoclass:: molecule.command.init.template.Template()
   :undoc-members:

.. _lint:

Lint
^^^^

.. autoclass:: molecule.command.lint.Lint()
   :undoc-members:

.. _list:

List
^^^^

.. autoclass:: molecule.command.list.List()
   :undoc-members:

.. _login:

Login
^^^^^

.. autoclass:: molecule.command.login.Login()
   :undoc-members:

.. _matrix:

Matrix
^^^^^^

Matrix will display the subcommand's ordered list of actions, which can be
changed in `scenario`_ configuration.

.. _`scenario`: https://molecule.readthedocs.io/en/latest/configuration.html#scenario

.. autoclass:: molecule.command.matrix.Matrix()
   :undoc-members:

.. _prepare:

Prepare
^^^^^^^

.. autoclass:: molecule.command.prepare.Prepare()
   :undoc-members:

.. _side-effect:

Side Effect
^^^^^^^^^^^

.. autoclass:: molecule.command.side_effect.SideEffect()
   :undoc-members:

.. _syntax:

Syntax
^^^^^^

.. autoclass:: molecule.command.syntax.Syntax()
   :undoc-members:

.. _test:

Test
^^^^

Test will execute the sequence necessary to test the instances.

.. autoclass:: molecule.command.test.Test()
   :undoc-members:

.. _verify:

Verify
^^^^^^

.. autoclass:: molecule.command.verify.Verify()
   :undoc-members:
