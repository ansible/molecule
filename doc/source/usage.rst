Usage
=====

Quick Start
^^^^^^^^^^^

Install Molecule using pip:

.. code-block:: bash

    $ pip install ansible
    $ pip install docker-py
    $ pip install molecule --pre

Create a new role:

.. code-block:: bash

    $ molecule init role --role-name foo
    --> Initializing new role foo...
    Initialized role in /tmp/foo successfully.

Or Create a new scenario in an existing role:

.. code-block:: bash

    $ cd foo
    $ molecule init scenario --role-name foo --scenario-name new-scenario
    --> Initializing new scenario new-scenario...
    Initialized scenario in /tmp/foo/molecule/new-scenario successfully.

1. Update the role with needed functionality and tests.
2. Install the dependencies by following the instructions in `INSTALL.rst`
   included in the role's scenario directory.
3. Now test it.

.. code-block:: bash

    $ cd foo
    $ molecule test
    --> Test matrix

    └── default
        ├── destroy
        ├── dependency
        ├── syntax
        ├── create
        ├── converge
        ├── idempotence
        ├── lint
        ├── side_effect
        ├── verify
        └── destroy
    --> Scenario: 'default'
    --> Term: 'destroy'

        PLAY [Destroy] *****************************************************************

        TASK [Destroy molecule instance(s)] ********************************************
        ok: [localhost] => (item=(censored due to no_log))

        PLAY RECAP *********************************************************************
        localhost                  : ok=1    changed=0    unreachable=0    failed=0


    --> Scenario: 'default'
    --> Term: 'dependency'
    --> Scenario: [default]
    --> Dependency: [galaxy]
    Skipping, missing the requirements file.
    --> Scenario: 'default'
    --> Term: 'syntax'

        playbook: /Users/jodewey/git/molecule_2/test/scenarios/foo/molecule/default/playbook.yml

    --> Scenario: 'default'
    --> Term: 'create'

        PLAY [Create] ******************************************************************

        TASK [Create Dockerfiles from image names] *************************************
        changed: [localhost] => (item=(censored due to no_log))

        TASK [Build an Ansible compatible image] ***************************************
        changed: [localhost] => (item=(censored due to no_log))

        TASK [Create molecule instance(s)] *********************************************
        changed: [localhost] => (item=(censored due to no_log))

        PLAY RECAP *********************************************************************
        localhost                  : ok=3    changed=3    unreachable=0    failed=0


    --> Scenario: 'default'
    --> Term: 'converge'

        PLAY [Converge] ****************************************************************

        TASK [Gathering Facts] *********************************************************
        ok: [instance]

        PLAY RECAP *********************************************************************
        instance                   : ok=1    changed=0    unreachable=0    failed=0


    --> Scenario: 'default'
    --> Term: 'idempotence'
    Idempotence completed successfully.
    --> Scenario: 'default'
    --> Term: 'lint'
    --> Executing Yamllint on files found in /Users/jodewey/git/molecule_2/test/scenarios/foo/...
    Lint completed successfully.
    --> Executing Flake8 on files found in /Users/jodewey/git/molecule_2/test/scenarios/foo/molecule/default/tests/...
    Lint completed successfully.
    --> Executing Ansible Lint on /Users/jodewey/git/molecule_2/test/scenarios/foo/molecule/default/playbook.yml...
    Lint completed successfully.
    --> Scenario: 'default'
    --> Term: 'side_effect'
    Skipping, side effect playbook not configured.
    --> Scenario: 'default'
    --> Term: 'verify'
    --> Executing Testinfra tests found in /Users/jodewey/git/molecule_2/test/scenarios/foo/molecule/default/tests/...
        ============================= test session starts ==============================
        platform darwin -- Python 2.7.13, pytest-3.0.7, py-1.4.33, pluggy-0.4.0
        rootdir: /Users/jodewey/git/molecule_2, inifile: pytest.ini
        plugins: testinfra-1.6.0, verbose-parametrize-1.2.2, mock-1.6.0, helpers-namespace-2016.7.10, cov-2.4.0
    collected 1 itemss

        tests/test_default.py .

        ============================ pytest-warning summary ============================
        WP1 None Module already imported so can not be re-written: testinfra
        ================= 1 passed, 1 pytest-warnings in 5.31 seconds ==================
    Verifier completed successfully.
    --> Scenario: 'default'
    --> Term: 'destroy'

        PLAY [Destroy] *****************************************************************

        TASK [Destroy molecule instance(s)] ********************************************
        changed: [localhost] => (item=(censored due to no_log))

        PLAY RECAP *********************************************************************
        localhost                  : ok=1    changed=1    unreachable=0    failed=0

Check
^^^^^

.. autoclass:: molecule.command.check.Check()
   :undoc-members:

Converge
^^^^^^^^

Converge will execute the sequence necessary to converge the instances.

.. autoclass:: molecule.command.converge.Converge()
   :undoc-members:

Create
^^^^^^

.. autoclass:: molecule.command.create.Create()
   :undoc-members:

Dependency
^^^^^^^^^^

.. autoclass:: molecule.command.dependency.Dependency()
   :undoc-members:

Destroy
^^^^^^^

.. autoclass:: molecule.command.destroy.Destroy()
   :undoc-members:

Idempotence
^^^^^^^^^^^

.. autoclass:: molecule.command.idempotence.Idempotence()
   :undoc-members:

Init
^^^^

.. autoclass:: molecule.command.init.role.Role()
   :undoc-members:

.. autoclass:: molecule.command.init.scenario.Scenario()
   :undoc-members:

.. autoclass:: molecule.command.init.template.Template()
   :undoc-members:

Lint
^^^^

.. autoclass:: molecule.command.lint.Lint()
   :undoc-members:

List
^^^^

.. autoclass:: molecule.command.list.List()
   :undoc-members:

Login
^^^^^

.. autoclass:: molecule.command.login.Login()
   :undoc-members:

Side Effect
^^^^^^^^^^^

.. autoclass:: molecule.command.side_effect.SideEffect()
   :undoc-members:

Syntax
^^^^^^

.. autoclass:: molecule.command.syntax.Syntax()
   :undoc-members:

Test
^^^^

Test will execute the sequence necessary to test the instances.

.. autoclass:: molecule.command.test.Test()
   :undoc-members:

Verify
^^^^^^

.. autoclass:: molecule.command.verify.Verify()
   :undoc-members:
