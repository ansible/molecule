.. _getting-started:

*********************
Getting Started Guide
*********************

The following guide will step through an example of developing and testing an
new role from scratch. After reading this guide, you should be familiar with
all the basics of how to use Molecule and what it can offer you.

.. note::

    In order to complete this guide by hand, you will need to additionally
    install `Docker`_.

.. _Docker: https://docs.docker.com/

Creating a new role
-------------------

Molecule uses `Ansible Galaxy`_ under the hood to generate conventional role
layouts. If you've ever worked with roles before, you'll be right at home. If
not, please review the `Role directory structure`_ guide to see what each
folder is responsible for.

.. _Ansible Galaxy: https://docs.ansible.com/ansible/latest/reference_appendices/galaxy.html#the-command-line-tool
.. _Role directory structure: https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html#role-directory-structure

To generate a new role with Molecule, just run:

.. code-block:: bash

    $ molecule init role -r my-new-role

Molecule Scenarios
------------------

You will notice one new folder which is the ``molecule`` folder.

In this folder is a single :ref:`root_scenario` called ``default``.

A scenario is a test suite for your newly created role. We can imagine that if
we are creating a role to install and configure the MySQL relational database
then we might have a number of scenarios. A scenario to test against version
5.6 on CentOS, another with version 5.7 on Debian and so on.

The Scenario Layout
-------------------

Within the ``molecule/default`` folder, we find a number of files:

.. code-block:: bash

    $ ls
    Dockerfile.j2  INSTALL.rst  molecule.yml  playbook.yml  tests

* Since `Docker`_ is the default :ref:`driver`, we find a ``Dockerfile.j2``
  `Jinja2`_ template file in place. Molecule will use this file to build a
  container with which to test your role against.

* ``INSTALL.rst`` contains instructions on what additional software or setup
  steps you will need to take in order to allow Molecule to successfully
  interface with the driver.

* ``molecule.yml`` is the central configuration entrypoint for Molecule. With
  this file, you can configure each tool that Molecule will employ when testing
  your role.

* ``playbook.yml`` is the playbook file that contains the call site for your
  role. Molecule will invoke this playbook with ``ansible-playbook`` and run it
  against your newly created Docker container.

* ``tests`` is the tests folder created because Molecule uses `testinfra`_ as
  the default :ref:`verifier`. This allows you to write specific tests against the
  state of the container after your role has finished executing. Other verifier
  tools are available.

.. _Docker: https://docs.docker.com/
.. _Jinja2: http://jinja.pocoo.org/
.. _testinfra: https://testinfra.readthedocs.io/

Inspecting the ``molecule.yml``
-------------------------------

The ``molecule.yml`` is for configuring Molecule. It is a `YAML`_ file whose
keys represent the high level components that Molecule provides. These are:

* The :ref:`dependency` manager. Molecule uses `Ansible Galaxy`_ by default to
  resolve your role dependencies.

* The :ref:`driver` provider. Molecule uses `Docker`_ by default. Molecule uses
  the driver to delegate the task of creating instances. There are many
  providers such as :ref:`azure-driver` , :ref:`ec2-driver`, :ref:`gce-driver`
  and :ref:`linode-driver`. Under the hood, it's all Ansible modules.

* The :ref:`lint` provider. Molecule uses `yamllint`_ by default to ensure that
  best practices are encouraged when writing YAML.

* The :ref:`platforms` definitions. Molecule relies on this to know which
  instances to create, name and to which group each instance belongs.

* The :ref:`provisioner`. Molecule only provides an Ansible provisioner.
  Ansible manages the life cycle of the instance based on this configuration.

* The :ref:`root_scenario` defintion. Molecule relies on this configuration to
  control the scenario steps order and sequencing.

* The :ref:`verifier` framework. Molecule uses `testinfra`_ by default to
  provide a way to write specific state checking tests (such as deployment
  smoke tests) on the target instance.

.. _YAML:  https://yaml.org/
.. _yamllint: http://yamllint.readthedocs.io/
.. _Ansible Galaxy: https://docs.ansible.com/ansible/latest/reference_appendices/galaxy.html#the-command-line-tool
.. _Docker: https://docs.docker.com/

Run test sequence commands
--------------------------

Let's create the first instance.

First, ensure that `Docker`_ is running with:

.. code-block:: bash

    $ docker --version

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

Finally, we can exit the instance and destroy it with:

.. code-block:: bash

    $ molecule destroy

Run a full test sequence
------------------------

In the previous section, we saw that there are many commands that Molecule
provides for manually managing the lifecyle of your instance, scenario,
development and testing tools. However, we can also tell Molecule to manage
this automatically within a :ref:`root_scenario` sequence.

The full lifecycle sequence can be invoked with:

.. code-block:: bash

    $ molecule test

.. note::

    It can be particularly useful to pass the ``--destroy=never`` flag when
    invoking ``molecule test`` so that you can tell Molecule to run the full
    sequence but not destroy the instance if one step fails.

Next Steps
----------

We've covered a lot of concepts and vocabulary that Molecule provides as
well as the functionality it provides. To keep learning, please review
the :ref:`common-use-cases` documentation.
