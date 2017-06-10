Configuration
=============

Config
------

.. autoclass:: molecule.config.Config
   :undoc-members:

Variable Substitution
---------------------

.. autoclass:: molecule.interpolation.Interpolator
   :undoc-members:

Dependency
----------

Testing roles may rely upon additional dependencies.  Molecule handles managing
these dependencies by invoking configurable dependency managers.

Ansible Galaxy
^^^^^^^^^^^^^^

.. autoclass:: molecule.dependency.ansible_galaxy.AnsibleGalaxy
   :undoc-members:

Gilt
^^^^

.. autoclass:: molecule.dependency.gilt.Gilt
   :undoc-members:

Driver
------

Molecule uses `Ansible`_ to manage instances to operate on.  Molecule supports
any provider `Ansible`_ supports.  This work is offloaded to the `provisioner`.

The driver's name is specified in `molecule.yml`, and can be overriden on the
command line.  Molecule will remember the last successful driver used, and
continue to use the driver for all subsequent subcommands, or until the
instances are destroyed by Molecule.

.. important::

    The verifier must support the Ansible provider for proper Molecule
    integration.

    The driver's python package requires installation.

.. _`Ansible`: https://docs.ansible.com

Docker
^^^^^^

.. autoclass:: molecule.driver.dockr.Dockr
   :undoc-members:

EC2
^^^

.. autoclass:: molecule.driver.ec2.Ec2
   :undoc-members:

LXC
^^^

.. autoclass:: molecule.driver.lxc.Lxc
   :undoc-members:

LXD
^^^

.. autoclass:: molecule.driver.lxd.Lxd
   :undoc-members:

Openstack
^^^^^^^^^

.. autoclass:: molecule.driver.openstack.Openstack
   :undoc-members:

Static
^^^^^^

.. autoclass:: molecule.driver.static.Static
   :undoc-members:

Vagrant
^^^^^^^

.. autoclass:: molecule.driver.vagrant.Vagrant
   :undoc-members:

Molecule Vagrant Module 
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    - hosts: localhost
      connection: local
      tasks:
        - name: Create instances
          molecule_vagrant:
            instance_name: "{{ item }}"
            platform_box: ubuntu/trusty64
            molecule_file: "{{ molecule_file }}"
            state: up
          with_items:
            - instance-1
            - instance-2

    - hosts: localhost
      connection: local
      tasks:
        - name: Destroy instances
          molecule_vagrant:
            instance_name: "{{ item }}"
            platform_box: ubuntu/trusty64
            molecule_file: "{{ molecule_file }}"
            state: destroy
          with_items:
            - instance-1
            - instance-2

    - hosts: localhost
      connection: local
      tasks:
        - name: Create instance with interfaces
          molecule_vagrant:
            instance_name: instance-1
            instance_interfaces:
              - auto_config: true
                network_name: private_network
                type: dhcp
              - auto_config: false
                network_name: private_network
                type: dhcp
              - auto_config: true
                ip: 192.168.11.3
                network_name: private_network
                type: static
            platform_box: ubuntu/trusty64
            molecule_file: "{{ molecule_file }}"
            state: destroy


Lint
----

Molecule handles role linting by invoking configurable linters.

Ansible Lint
^^^^^^^^^^^^

.. autoclass:: molecule.lint.ansible_lint.AnsibleLint
   :undoc-members:

Platforms
---------

.. autoclass:: molecule.platforms.Platforms
   :undoc-members:

Provisioner
-----------

Molecule handles provisioning and converging the role.

Ansible
^^^^^^^

.. autoclass:: molecule.provisioner.ansible.Ansible
   :undoc-members:

Scenario
--------

Molecule treats scenarios as a first-class citizens, with a top-level
configuration syntax.

.. autoclass:: molecule.scenario.Scenario
   :undoc-members:

State
-----

.. autoclass:: molecule.state.State
   :undoc-members:

Verifier
--------

Molecule handles role testing by invoking configurable verifiers.

Goss
^^^^

.. autoclass:: molecule.verifier.goss.Goss
   :undoc-members:

Testinfra
^^^^^^^^^

.. autoclass:: molecule.verifier.flake8.Flake8
   :undoc-members:

.. autoclass:: molecule.verifier.testinfra.Testinfra
   :undoc-members:
