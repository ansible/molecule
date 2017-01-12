Usage
=====

Quick Start
^^^^^^^^^^^

Install Molecule using pip:

.. code-block:: bash

  $ pip install molecule --pre

.. warn::

    This install method is not yet available.  We will cut a pre-release
    candidate once ready.

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
  --> Scenario: [default]
  --> Provisioner: [ansible]
  --> Playbook: [destroy.yml]

  PLAY [localhost] ***************************************************************

  TASK [setup] *******************************************************************
  ok: [localhost]

  TASK [Destroy molecule instance(s)] ********************************************
  changed: [localhost] => (item={'name': u'instance-1'})

  PLAY RECAP *********************************************************************
  localhost                  : ok=2    changed=1    unreachable=0    failed=0

  --> Scenario: [default]
  --> Dependency: [galaxy]
  --> Scenario: [default]
  --> Provisioner: [ansible]
  --> Syntax Verification of Playbook: [playbook.yml]

  playbook: /Users/jodewey/git/molecule_2/test/scenarios/docker/molecule/default/playbook.yml
  --> Scenario: [default]
  --> Provisioner: [ansible]
  --> Playbook: [create.yml]

  PLAY [localhost] ***************************************************************

  TASK [setup] *******************************************************************
  ok: [localhost]

  TASK [Build an Ansible compatible image] ***************************************
  ok: [localhost]

  TASK [Create molecule instance(s)] *********************************************
  changed: [localhost] => (item={'name': u'instance-1'})

  PLAY RECAP *********************************************************************
  localhost                  : ok=3    changed=1    unreachable=0    failed=0

  --> Scenario: [default]
  --> Provisioner: [ansible]
  --> Playbook: [playbook.yml]

  PLAY [all] *********************************************************************

  TASK [setup] *******************************************************************
  ok: [instance-1-default]

  PLAY RECAP *********************************************************************
  instance-1-default         : ok=1    changed=0    unreachable=0    failed=0

  --> Scenario: [default]
  --> Provisioner: [ansible]
  --> Idempotence Verification of Playbook: [playbook.yml]
  Idempotence test passed.
  --> Scenario: [default]
  --> Lint: [ansible-lint]
  --> Scenario: [default]
  --> Verifier: [testinfra]
  --> Executing flake8 on files found in /Users/jodewey/git/molecule_2/test/scenarios/docker/molecule/default/tests/...
  --> Executing testinfra tests found in /Users/jodewey/git/molecule_2/test/scenarios/docker/molecule/default/tests/...
  ============================= test session starts ==============================
  platform darwin -- Python 2.7.12, pytest-3.0.5, py-1.4.31, pluggy-0.4.0
  rootdir: /Users/jodewey/git/molecule_2, inifile: pytest.ini
  plugins: testinfra-1.4.2, mock-1.5.0, helpers-namespace-2016.7.10, cov-2.4.0
  collecting 0 items collecting 1 items collected 1 items

  tests/test_default.py .

  ============================ pytest-warning summary ============================
  WP1 None Module already imported so can not be re-written: testinfra
  ================= 1 skipped, 1 pytest-warnings in 0.18 seconds =================
  --> Scenario: [default]
  --> Provisioner: [ansible]
  --> Playbook: [destroy.yml]

  PLAY [localhost] ***************************************************************

  TASK [setup] *******************************************************************
  ok: [localhost]

  TASK [Destroy molecule instance(s)] ********************************************
  changed: [localhost] => (item={'name': u'instance-1'})

  PLAY RECAP *********************************************************************
  localhost                  : ok=2    changed=1    unreachable=0    failed=0

Check
^^^^^

.. autoclass:: molecule.command.check.Check
   :undoc-members:
   :members: execute

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

Status
^^^^^^

.. autoclass:: molecule.command.status.Status
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

