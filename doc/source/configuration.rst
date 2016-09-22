*************
Configuration
*************

Molecule attempts to pick sane default configuration options (set internally),
however it's also possible to `override configuration`_, for example in
`~/.config/molecule/config.yml`.

Config file
===========

This file (molecule.yml), located in the role directory, contains all the
molecule-specific information for the role in the directory in which it's
located. It allows you to configure how molecule, ansible, verifiers, and
drivers will behave. This information is contained in top level YAML sections
described below.

Molecule Section
----------------

The molecule section allows you to override molecule defaults.  This is is the
most specific setting for molecule and will override the contents of all other
config files. This is where you give molecule role-specific behavior.

.. code-block:: yaml

  molecule:
    raw_ssh_args:
      - -o StrictHostKeyChecking=false
      - -o UserKnownHostsFile=/dev/null

Ansible Section
---------------

In the ansible section, you can configure flags exactly as they're passed to
ansible-playbook. Please note, however, that commands that normally contain a
hyphen (-) will need to be replaced with an underscore (\_) to remain
compatible with YAML.

Values set to *False* will **NOT** be passed to `ansible-playbook`, but rather
will be skipped entirely. An example ansible section of `molecule.yml` may look
something like this:

.. code-block:: yaml

  ansible:
    inventory_file: ../../inventory/
    diff: False
    sudo: True
    vault_password_file: ~/.vault

As you can see, the names of these values correspond to what the underlying
`ansible-playbook` accepts. As such, as the functionality of Ansible grows,
support for new CLI options will be supported simply by adding its name: value
combination to the ansible section of your configuration.

The ansible section also supports a few values that aren't passed to
ansible-playbook in this way, but rather are passed as environment variables.
There are only a few currently in use.

.. code-block:: yaml

  ansible:
    config_file: /path/to/your/ansible.cfg
    playbook: /path/to/some/other_playbook.yml
    host_key_checking: False
    raw_ssh_args:
      - -o UserKnownHostsFile=/dev/null
      - -o IdentitiesOnly=yes
      - -o ControlMaster=auto
      - -o ControlPersist=60s
    raw_env_vars:
      ANSIBLE_ACTION_PLUGINS: ../plugins

The `raw_env_vars` section allows you to pass arbitrary environment variables
to ansible-playbook. This can be useful, for example, if you want to do a role
level override of a value normally found in ansible.cfg.

Host/Group Vars
^^^^^^^^^^^^^^^

Some playbooks require hosts/groups to have certain variables set. If you are
in this situation - simply add the `host_vars` and/or `group_vars` to the
ansible section. For example,

.. code-block:: yaml

  ansible:
    playbook: playbook.yml
    group_vars:
      foo1:
        - test: key
          var2: value
      foo2:
        - test: key
          var: value
    host_vars:
      foo1-01:
        - set_this_value: True

This example will set the variables for the ansible groups `foo1` and `foo2`.
For hosts `foo1-01` the value `set_this_value` will be set to True.

Native Inventory
^^^^^^^^^^^^^^^^

An alternative to the above `Host/Group Vars` is the creation of `group_vars`
and/or `host_vars` directories in the project root.  This allows ansible to
converge utilzing its built in group/host vars resolution.

Role Requirements
^^^^^^^^^^^^^^^^^

Testing roles may rely upon additional roles.  In this case adding
``requirements_file`` to the ansible section, will cause molecule to download
roles using `Ansible Galaxy`_.

Additional options can be passed to ``ansible-galaxy`` through the ``galaxy``
option under the ansible section.  Any option set in this section will override
the defaults.

.. _`Ansible Galaxy`: http://docs.ansible.com/ansible/galaxy.html

.. code-block:: yaml

  ansible:
    requirements_file: requirements.yml
    galaxy:
        ignore-certs: True
        ignore-errors: True

Vagrant Section
---------------

The other part of the configuration is the vagrant section. This is where you
will define what instances will be created, and how they will be configured.
Under the hood, molecule creates a Vagrantfile from a template and populates it
with the data you specify in this config.

Because it's impossible to support every Vagrant option, there are two places
where you can specify `raw\_config\_args.` The first is in the root of the
vagrant block, and this can be used for Vagrant options that are not supported
explicitly by Molecule currently - like configuring port forwarding to a guest
VM from your local machine.

The second place `raw\_config\_args` can be defined is within a specific
instance within the instances block. This allows you to define
instance-specific settings such as network interfaces with a config more
complicated than the interfaces section allows for.

Note: You can specify an options section for an instance. Currently, the only
key supported here is `append\_platform\_to\_hostname.` By setting this to 'no'
the platform name won't be appended to hostnames automatically, which is the
default. So, for example, an instance will simply be named vagrant-01 instead
of vagrant-01-rhel-7.

See Vagrant :ref:`vagrant_driver_usage`

Docker Section
--------------

Molecule supports docker too. If you want to test roles on containers, remove
the vagrant option or initialize your role with the ``--docker`` flag. Docker,
of course must be installed onto your system. The daemon does not need to be
running on your machine. Molecule will simply pull the environment variables
from your docker client. Also, the Ansible ``connection`` must be set to docker
with user root.

In order to use the docker driver, the image used must have at least one of the
following:

- apt-get/yum
- python 2.5+
- python 2.4 with python-simplejson

See Docker :ref:`docker_driver_usage`

OpenStack Section
-----------------

See OpenStack :ref:`openstack_driver_usage`

Driver Section
--------------

Multiple drivers can be specified in `molecule.yml`.  However, once instance(s)
are created, all subcommands must be run against the same driver, for the life
of the instance(s).

Drivers are found in the following order:

1. Supplying ``--driver=<driver>`` to certain subcommands.
2. The driver section from the config file.
3. Existing lookup order, by searching the config file for the presence of
   keys.

Usage
-----

.. code-block:: yaml

  ---
  driver:
    name: docker

.. note:: It is recommend to use the following syntax.  This matches
          test-kitchen, and will be further enhanced in molecule 2.x.

Verifier Section
----------------

See OpenStack :ref:`verifier_index`

Playbook
========

In general, your playbook.yml shouldn't require anything specific to molecule.
Rather, it should contain the logic you would like to apply in order to test
this particular role.

.. code-block:: yaml

  - hosts: all
    roles:
      - role: demo.molecule

Override Configuration
======================

1. project config
2. local config (``~/.config/molecule/config.yml``)
3. default config (``molecule.yml``)

The merge order is default -> local -> project, meaning that elements at the
top of the above list will be merged last, and have greater precedence than
elements at the bottom of the list.
