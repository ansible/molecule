Configuration
=============

Config
------

.. autoclass:: molecule.config.Config()
   :undoc-members:

Variable Substitution
---------------------

.. autoclass:: molecule.interpolation.Interpolator()
   :undoc-members:

Dependency
----------

Testing roles may rely upon additional dependencies.  Molecule handles managing
these dependencies by invoking configurable dependency managers.

Ansible Galaxy
^^^^^^^^^^^^^^

.. autoclass:: molecule.dependency.ansible_galaxy.AnsibleGalaxy()
   :undoc-members:

Gilt
^^^^

.. autoclass:: molecule.dependency.gilt.Gilt()
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

Azure
^^^^^

.. autoclass:: molecule.driver.azure.Azure()
   :undoc-members:

Delegated
^^^^^^^^^

.. autoclass:: molecule.driver.delegated.Delegated()
   :undoc-members:

Docker
^^^^^^

.. autoclass:: molecule.driver.docker.Docker()
   :undoc-members:

EC2
^^^

.. autoclass:: molecule.driver.ec2.Ec2()
   :undoc-members:

GCE
^^^

.. autoclass:: molecule.driver.gce.Gce()
   :undoc-members:

LXC
^^^

.. autoclass:: molecule.driver.lxc.Lxc()
   :undoc-members:

LXD
^^^

.. autoclass:: molecule.driver.lxd.Lxd()
   :undoc-members:

Openstack
^^^^^^^^^

.. autoclass:: molecule.driver.openstack.Openstack()
   :undoc-members:

Vagrant
^^^^^^^

.. autoclass:: molecule.driver.vagrant.Vagrant()
   :undoc-members:

.. _molecule_vagrant_module:

Molecule Vagrant Module
^^^^^^^^^^^^^^^^^^^^^^^

Molecule manages Vagrant via an internal Ansible module.  The following belongs
in the appropriate create or destroy playbooks, and uses the default provider.

Supported Providers:

* VirtualBox (default)
* VMware (vmware_fusion, vmware_workstation and vmware_desktop)
* Parallels

Create instances.

.. code-block:: yaml

    - hosts: localhost
      connection: local
      tasks:
        - name: Create instances
          molecule_vagrant:
            instance_name: "{{ item }}"
            platform_box: ubuntu/trusty64
            state: up
          with_items:
            - instance-1
            - instance-2

Destroy instances.

.. code-block:: yaml

    - hosts: localhost
      connection: local
      tasks:
        - name: Destroy instances
          molecule_vagrant:
            instance_name: "{{ item }}"
            platform_box: ubuntu/trusty64
            state: destroy
          with_items:
            - instance-1
            - instance-2

Create instances with interfaces.

.. code-block:: yaml

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
            state: destroy

Create instances with additional provider options.

.. code-block:: yaml

    - hosts: localhost
      connection: local
      tasks:
        - name: Create instances
          molecule_vagrant:
            instance_name: "{{ item }}"
            platform_box: ubuntu/trusty64
            provider_name: virtualbox
            provider_memory: 1024
            provider_cpus: 4
            provider_raw_config_args:
              - "customize ['modifyvm', :id, '--cpuexecutioncap', '50']"
            provider_options:
              gui: true
            state: up
          with_items:
            - instance-1
            - instance-2

Create instances with additional instance options.

.. code-block:: yaml

    - hosts: localhost
      connection: local
      tasks:
        - name: Create instances
          molecule_vagrant:
            instance_name: "{{ item }}"
            platform_box: ubuntu/trusty64
            instance_raw_config_args:
              - "vm.network 'forwarded_port', guest: 80, host: 8080"
            state: up
          with_items:
            - instance-1
            - instance-2

Lint
----

Molecule handles project linting by invoking configurable linters.

Yaml Lint
^^^^^^^^^

.. autoclass:: molecule.lint.yamllint.Yamllint()
   :undoc-members:

Platforms
---------

.. autoclass:: molecule.platforms.Platforms()
   :undoc-members:

Provisioner
-----------

Molecule handles provisioning and converging the role.

Ansible
^^^^^^^

.. autoclass:: molecule.provisioner.ansible.Ansible()
   :undoc-members:

Lint
....

Molecule handles provisioner linting by invoking configurable linters.

.. autoclass:: molecule.provisioner.lint.ansible_lint.AnsibleLint()
   :undoc-members:

.. _root_scenario:

Scenario
--------

Molecule treats scenarios as a first-class citizens, with a top-level
configuration syntax.

.. autoclass:: molecule.scenario.Scenario()
   :undoc-members:

Scenarios
---------

.. autoclass:: molecule.scenarios.Scenarios()
   :undoc-members:

State
-----

.. autoclass:: molecule.state.State()
   :undoc-members:

Verifier
--------

Molecule handles role testing by invoking configurable verifiers.

Goss
^^^^

.. autoclass:: molecule.verifier.goss.Goss()
   :undoc-members:

Lint
....

The Goss verifier does not utilize a linter.

Testinfra
^^^^^^^^^

.. autoclass:: molecule.verifier.testinfra.Testinfra()
   :undoc-members:

.. _root_lint:

Lint
....

Molecule handles test linting by invoking configurable linters.

.. autoclass:: molecule.verifier.lint.flake8.Flake8()
   :undoc-members:
