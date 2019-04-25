*************
Porting Guide
*************

Porting your existing role from Molecule to Molecule v2.

Automatically
=============

Molecule ships with a conversion script.  This conversion script converts a
molecule v1 vagrant driver config into a molecule v2 vagrant config.  The
script handles the creation of the initial directory structure, migration and
cleanup of files.

.. note::

    The script is fairly crude, and only supports Vagrant at the time of this
    writing.  The authors will be adding additional functionality as additional
    roles are migrated to v2.

.. code-block:: bash

    $ contrib/convert.py /path/to/v1/role/molecule.yml

Manually
========

1. In the basedir of your existing role, create a new ``default`` scenario.  This
   scenario is equivalent to your existing Molecule v1 setup.

.. code-block:: bash

    $ cd $role-name
    $ molecule init scenario -r $role-name -s default -d $driver-name

.. important:

    The linting checks will likely fail since the role was not created with
    ``molecule init role``.  The errors can be ignored by placing a ``.yamllint``
    file in the project root of the role.  This will be corrected in the
    future.

2. Move existing Testinfra tests to the new scenario's test directory located
   at ``molecule/default/tests/test_default.py``.

3. If necessary port existing Serverspec tests to Testinfra.  A Testinfra
   skeleton has been created at ``molecule/default/tests/test_default.py``.

4. Port role's existing ``molecule.yml`` to the new format located in the
   scenario's directory at `molecule/default/molecule.yml`.

5. Port role's existing ``playbook.yml`` to the new location in the scenario's
   directory at `molecule/default/playbook.yml`.

6. Cleanup

.. code-block:: bash

    $ rm -rf .molecule/
    $ rm -rf molecule.yml
    $ rm -rf playbook.yml
    $ rm -rf tests/

6. Test

.. code-block:: bash

    $ molecule test
