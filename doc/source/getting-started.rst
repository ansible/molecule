.. _getting-started:

*********************
Getting Started Guide
*********************

The following guide will step through an example of developing and testing a
new Ansible role. After reading this guide, you should be familiar with the
basics of how to use Molecule and what it can offer.

.. contents::

.. note::

    In order to complete this guide by hand, you will need to additionally
    install `Docker`_. Molecule requires an external Python dependency for the
    Docker driver which is provided when installing Molecule using ``pip
    install 'molecule[docker]'``.

.. _Docker: https://docs.docker.com/

Creating a new role
-------------------

Molecule uses :std:doc:`reference_appendices/galaxy` under the hood to
generate conventional role layouts. If you've ever worked with Ansible roles
before, you'll be right at home. If not, please review the
:std:doc:`user_guide/playbooks_reuse_roles` guide to see what each folder is
responsible for.

To generate a new role with Molecule, simply run:

.. code-block:: bash

    $ molecule init role -r my-new-role

You should then see a ``my-new-role`` folder in your current directory.

.. note::

    For future reference, if you want to initialize Molecule within an
    existing role, you would use the ``molecule init scenario -r
    my-role-name`` command.

Molecule Scenarios
------------------

You will notice one new folder which is the ``molecule`` folder.

In this folder is a single :ref:`root_scenario` called ``default``.

Scenarios are the starting point for a lot of powerful functionality that
Molecule offers. For now, we can think of a scenario as a test suite for your
newly created role. You can have as many scenarios as you like and Molecule
will run one after the other.

The Scenario Layout
-------------------

Within the ``molecule/default`` folder, we find a number of files and
directories:

.. code-block:: bash

    $ ls
    Dockerfile.j2  INSTALL.rst  molecule.yml  playbook.yml  tests

* Since `Docker`_ is the default :ref:`driver`, we find a ``Dockerfile.j2``
  `Jinja2`_ template file in place. Molecule will use this file to build a
  docker image to test your role against.

* ``INSTALL.rst`` contains instructions on what additional software or setup
  steps you will need to take in order to allow Molecule to successfully
  interface with the driver.

* ``molecule.yml`` is the central configuration entrypoint for Molecule. With
  this file, you can configure each tool that Molecule will employ when testing
  your role.

* ``playbook.yml`` is the playbook file that contains the call site for your
  role. Molecule will invoke this playbook with ``ansible-playbook`` and run it
  against an instance created by the driver.

* ``tests`` is the tests directory created because Molecule uses
  :std:doc:`TestInfra <testinfra:index>` as the default :ref:`verifier`. This
  allows you to write specific tests against the state of the container after
  your role has finished executing. Other verifier tools are available.

.. _Jinja2: http://jinja.pocoo.org/

Inspecting the ``molecule.yml``
-------------------------------

The ``molecule.yml`` is for configuring Molecule. It is a `YAML`_ file whose
keys represent the high level components that Molecule provides. These are:

* The :ref:`dependency` manager. Molecule uses
  :std:doc:`reference_appendices/galaxy` by default to resolve your role
  dependencies.

* The :ref:`driver` provider. Molecule uses `Docker`_ by default. Molecule uses
  the driver to delegate the task of creating instances. There are many
  providers such as :ref:`azure-driver` , :ref:`ec2-driver`, :ref:`gce-driver`
  and :ref:`linode-driver`. Under the hood, it's all Ansible modules.

* The :ref:`linters` provider. Molecule uses :std:doc:`Yamllint
  <yamllint:index>` by default to ensure that best practices are encouraged
  when writing YAML.

* The :ref:`platforms` definitions. Molecule relies on this to know which
  instances to create, name and to which group each instance belongs. If you
  need to test your role against multiple popular distributions (CentOS,
  Fedora, Debian), you can specify that in this section.

* The :ref:`provisioner`. Molecule only provides an Ansible provisioner.
  Ansible manages the life cycle of the instance based on this configuration.

* The :ref:`root_scenario` definition. Molecule relies on this configuration
  to control the scenario sequence order.

* The :ref:`verifier` framework. Molecule uses :std:doc:`TestInfra
  <testinfra:index>` by default to provide a way to write specific state
  checking tests (such as deployment smoke tests) on the target instance.

.. _YAML:  https://yaml.org/

Run test sequence commands
--------------------------

Let's create the first Molecule managed instance with the Docker driver.

First, ensure that `Docker`_ is running with the typical sanity check:

.. code-block:: bash

    $ docker run hello-world

Now, we can tell Molecule to create an instance with:

.. code-block:: bash

    $ molecule create

We can verify that Molecule has created the instance and they're up and running with:

.. code-block:: bash

    $ molecule list

Now, let's add a task to our ``tasks/main.yml`` like so:

.. code-block:: yaml

    - name: Molecule Hello World!
      debug:
        msg: Hello, World!

We can then tell Molecule to test our role against our instance with:

.. code-block:: bash

    $ molecule converge

If we want to manually inspect the instance afterwards, we can run:

.. code-block:: bash

    $ molecule login

We now have a free hand to experiment with the instance state.

Finally, we can exit the instance and destroy it with:

.. code-block:: bash

    $ molecule destroy

.. note::

   If Molecule reports any errors, it can be useful to pass the ``--debug``
   option to get more verbose output.

Run a full test sequence
------------------------

Molecule provides commands for manually managing the lifecyle of the instance,
scenario, development and testing tools. However, we can also tell Molecule to
manage this automatically within a :ref:`root_scenario` sequence.

The full lifecycle sequence can be invoked with:

.. code-block:: bash

    $ molecule test

.. note::

    It can be particularly useful to pass the ``--destroy=never`` flag when
    invoking ``molecule test`` so that you can tell Molecule to run the full
    sequence but not destroy the instance if one step fails.
