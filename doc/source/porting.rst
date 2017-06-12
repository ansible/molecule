*************
Porting Guide
*************

Porting your existing role from Molecule to Molecule v2.  As of this writing
this is a manual process.

1. In the basedir of your existing role, create a new `default` scenario.  This
   scenario is equivalent to your existing Molecule v1 setup. 

.. code-block:: bash

    $ cd $role-name
    $ molecule init scenario --role-name $role-name  --scenario-name default --driver-name $driver-name

2. Move existing Testinfra tests to the new scenario's test directory located
   at `molecule/default/tests/test_default.py`.

3. If necessary port existing Serverspec tests to Testinfra.  A Testinfra
   skeleton has been created at `molecule/default/tests/test_default.py`.

4. Port role's existing `molecule.yml` to the new format located in the
   scenario's directory at `molecule/default/molecule.yml`.

5. Port role's existing `playbook.yml` to the new location in the scenario's
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
