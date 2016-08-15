Usage
=====

Installation
------------

Molecule is distributed as a python package, so you can use familiar methods to
manage your installation:

* Install from `PyPI`_ with `pip`

  .. code-block:: bash

      pip install molecule

* Optionally in a `virtual environment`_

.. _`PyPI`: http://python-packaging-user-guide.readthedocs.org/en/latest/installing/#installing-from-pypi
.. _`virtual environment`: http://python-packaging-user-guide.readthedocs.org/en/latest/installing/#creating-virtual-environments

Installing from source
^^^^^^^^^^^^^^^^^^^^^^

Due to the rapid pace of development on this tool, you might want to
install it in "`development`_" mode so that new updates can be obtained by
simply doing a ``git pull`` in the repository's directory.

.. code-block:: bash

    cd /path/to/repos
    git clone git@github.com:metacloud/molecule.git
    cd molecule
    sudo python setup.py develop

There is also a `pip pattern` for development mode:

.. code-block:: bash

    cd /path/to/repos
    git clone git@github.com:metacloud/molecule.git
    pip install -U -e molecule/

Bash Completion
^^^^^^^^^^^^^^^

A bash completion script is provided in the assets directory. It auto-completes
the subcommands, options and dynamic arguments such as platform, providers, and
hosts.

Linux users
"""""""""""
The script will install globally in ``etc/bash_completion.d``.

OS X users
""""""""""

For OS X user, you must do the following to enable the script:

.. code-block:: bash

  USER_BASH_COMPLETION_DIR=~/bash_completion.d
  mkdir -p "${USER_BASH_COMPLETION_DIR}"
  wget -O "${USER_BASH_COMPLETION_DIR}/molecule" https://github.com/metacloud/molecule/blob/master/assets/bash_completion/molecule.bash-completion.sh

and in ``~/.bash_profile``, add the following:

.. code-block:: bash

  if [ -d ~/bash_completion.d ]; then
    . ~/bash_completion.d/*
  fi

if you are using ``brew`` you can use ``${BASH_COMPLETION_DIR}`` instead of
``${USER_BASH_COMPLETION_DIR}``.

Dependencies
------------

Molecule relies on several outside packages and programs to function.

- `Ansible`_
- `Vagrant`_
- `Serverspec`_
- `Testinfra`_
- `Rubocop`_
- `Rake`_

Configuration
-------------

In order to be compatible with Molecule, a role will require some basic
structure.

::

    role_name/
    ├── molecule.yml
    └── playbook.yml

Optionally, if you want to test with `Serverspec`_, you will need::

    role_name/
    ├── ...
    └── spec/
        ├── spec_helper.rb
        └── default_spec.rb

Optionally, if you want to test with `Testinfra`_, you will need::

    role_name/
    ├── ...
    └── tests/
        └── test_*.py


Molecule attempts to pick sane default configuration options (set
internally), however it's also possible to `override configuration`_,
for example in `~/.config/molecule/config.yml`.
Here is a commented example:

.. literalinclude:: ../../molecule/conf/defaults.yml
   :language: yaml

molecule.yml
------------

This file, located in the role directory, contains all the molecule-specific
information for the role in the directory in
which it's located. It allows you to configure how molecule, vagrant and
ansible will behave. This information is contained in 3 top level YAML
sections: molecule, ansible and vagrant.

The molecule section allows you to override molecule defaults, much like you
might do in a `config.yml` for molecule. This is is the most specific setting
for molecule and will override the contents of all other config files. This
is where you give molecule role-specific behavior.

.. code-block:: yaml

    molecule:
      raw_ssh_args:
        - -o StrictHostKeyChecking=false
        - -o UserKnownHostsFile=/dev/null


Ansible
-------

In the ansible section, you can configure flags exactly as they're
passed to ansible-playbook. Please note, however, that commands that
normally contain a hyphen (-) will need to be replaced with an underscore
(\_) to remain compatible with YAML.

Values set to *False* will **NOT** be passed to `ansible-playbook`, but
rather will be skipped entirely. An example ansible section of
`molecule.yml` may look something like this:

.. code-block:: yaml

    ansible:
      inventory_file: ../../inventory/
      diff: False
      sudo: True
      vault_password_file: ~/.vault

As you can see, the names of these values correspond to what the
underlying `ansible-playbook` accepts. As such, as the functionality of
Ansible grows, support for new CLI options will be supported simply by
adding its name: value combination to the ansible section of your
configuration.

The ansible section also supports a few values that aren't passed to
ansible-playbook in this way, but rather are passed as environment
variables. There are only a few currently in use.

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

The `raw_env_vars` section allows you to pass arbitrary environment
variables to ansible-playbook. This can be useful, for example, if you
want to do a role level override of a value normally found in
ansible.cfg.


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

This example will set the variables for the ansible groups `foo1`
and `foo2`. For hosts `foo1-01` the value `set_this_value` will be
set to True.

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

Vagrant
-------

The other part of the configuration is the vagrant section. This is
where you will define what instances will be created, and how they will
be configured. Under the hood, molecule creates a Vagrantfile from a
template and populates it with the data you specify in this config.

Because it's impossible to support every Vagrant option, there are two
places where you can specify `raw\_config\_args.` The first is in the
root of the vagrant block, and this can be used for Vagrant options that
are not supported explicitly by Molecule currently - like
configuring port forwarding to a guest VM from your local machine.

The second place `raw\_config\_args` can be defined is within a specific
instance within the instances block. This allows you to define
instance-specific settings such as network interfaces with a config more
complicated than the interfaces section allows for.

Note: You can specify an options section for an instance. Currently, the
only key supported here is `append\_platform\_to\_hostname.` By setting
this to 'no' the platform name won't be appended to hostnames
automatically, which is the default. So, for example, an instance will
simply be named vagrant-01 instead of vagrant-01-rhel-7.

.. code:: yaml

    vagrant:
      raw_config_args:
        - "ssh.insert_key = false"
        - "vm.network 'forwarded_port', guest: 80, host: 8080"

      platforms:
        - name: trusty64
          box: trusty64
          box_url: https://vagrantcloud.com/ubuntu/boxes/trusty64/versions/14.04/providers/virtualbox.box

      providers:
        - name: virtualbox
          type: virtualbox
          options:
            memory: 512
            cpus: 2

      instances:
        - name: vagrant-01
          ansible_groups:
            - group_1
            - group_2
          interfaces:
            - network_name: private_network
              type: dhcp
              auto_config: true
            - network_name: private_network
              type: static
              ip: 192.168.0.1
              auto_config: true
          options:
            append_platform_to_hostname: no
          raw_config_args:
            - "vm.network 'private_network', type: 'dhcp', auto_config: false"

A ``box_url`` is not required - if the vagrant box is available on hashicorp,
it can be specified in ``box``. For example, the same image in the previous
example can be invoked like so:

.. code:: yaml

  platforms:
    - name: trusty64
    box: ubuntu/trusty64

Docker
------
Molecule supports docker too. If you want to test roles on containers, remove
the vagrant option or initialize your role with the ``--docker`` flag. Docker,
of course must be installed onto your system. The daemon does not need to be
running on your machine. Molecule will simply pull the environment variables
from your docker client. Also, the Ansible ``connection`` must be set to docker
with user root.

In order to use the docker driver, the image used must have at least one
of the following:

- apt-get/yum
- python 2.5+
- python 2.4 with python-simplejson

Here is an example of a complete ``molecule.yml`` with 2 containers.

.. code-block:: yaml

  ---
  docker:
    containers:
      - name: foo-01
        ansible_groups:
          - group1
        image: ubuntu
        image_version: latest
      - name: foo-02
        ansible_groups:
          - group2
        image: ubuntu
        image_version: '14.04'

Note: numeric versions need to be put in quotes. If the image version tag is
not a number, it does not need to be in quotes.

A specific registry can also be defined with the ``registry`` option in the
container.  When accessing a private registry, ensure your docker client is
logged into whichever registry you are trying to access.

Testinfra
---------

In the testinfra section, you can configure flags exactly as they're
passed to `testinfra`. Some flags, such as ``ansible-inventory``,
``connection`` and ``hosts``, are already set by Molecule. Any flag
set in this section will override the defaults. See more details on
using `testinfra's command line arguments`_.

.. code-block:: yaml

    testinfra:
      n: 1


Note: Testinfra is based on pytest, so additional `pytest arguments`_ can be
passed through it.

.. _`testinfra's command line arguments`: http://testinfra.readthedocs.io/en/latest/invocation.html
.. _`PyTest arguments`: http://pytest.org/latest/usage.html#usage

playbook.yml
------------

In general, your playbook.yml shouldn't require anything specific to
molecule. Rather, it should contain the logic you would like to apply in
order to test this particular role.

.. code-block:: yaml

    - hosts: all
      roles:
        - role: demo.molecule

Override Configuration
----------------------

1. project config
2. local config (``~/.config/molecule/config.yml``)
3. default config (``molecule.yml``)

The merge order is default -> local -> project, meaning that elements at
the top of the above list will be merged last, and have greater precedence
than elements at the bottom of the list.

Using Molecule In Travis
------------------------

`Travis`_ is an excellent CI platform for testing Ansible roles. With the
docker driver, molecule can easily be used to test multiple configurations
on Travis. Here is an example of a ``.travis.yml`` that is used to test a role
named foo1. In this example, the role ``foo1`` uses the docker driver and
is assumed to be in the directory ``roledir/foo1`` with the proper
``molecule.yml``.

.. code-block:: yaml

  sudo: required

  language: python

  services:
    - docker

  before_install:
  - sudo apt-get -qq update
  - sudo apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y docker-engine

  install:
  - pip install molecule

  script:
  - cd roledir/foo1
  - molecule test


Usage
-----

In the contexts of operations and virtualization, the word 'provision'
tends to refer to the initial creation of machines by allocating (hardware)
resources; in contrast, in the context of configuration management
(and in vagrant), 'provisioning' refers to taking the (virtual) machine
from an initial boot to having run the configuration management system
(Ansible, Salt, Puppet, Chef CFEngine or just shell). Molecule uses the term
'converge' (as does Test Kitchen) to refer to this latter meaning of
'provisioning' (i.e. "Run Ansible on the new test VM").

It is very simple to run tests using the molecule command from the working
directory of your role.

* ``molecule destroy``: Halts and destroys all instances associated with current role.
* ``molecule create``: Builds instances specified in molecule.yml.
* ``molecule converge``: Runs playbook.yml against instances associated with current
  role.
* ``molecule idempotence``: Checks output of ansible-playbook for "changed"/"failed".
* ``molecule verify``: Runs the functional tests (serverspec, testinfra).
* ``molecule login <host>``: Login to an instance via ssh.
* ``molecule init <role>``: Creates the directory structure and files for a new Ansible
  role compatible with molecule.
* ``molecule test``: Runs a series of commands to create, verify and destroy instances.

The exact sequence of commands run during the ``test`` command can be configured
in the `test['sequence']` config option.

The ``test`` command supports a ``--destroy`` argument that will accept the values
always, never, and passing. Use these to tune the behavior for various use cases.
For example, ``--destroy=always`` might be useful when using molecule for CI/CD.


Integration Testing
-------------------

Molecule supports testing using both `Serverspec`_ and `Testinfra`_. Tests
located in the ``spec/`` directory will be run by serverspec and tests
located in the ``tests/`` directory will be run by testinfra. Both of these
directories can be changed as molecule config options. Molecule will run
serverspec and testinfra if both directories are present.

When using serverspec, it's possible to target tests at the following
levels: all instances, specific groups, specific instances.

All files matching the pattern ``spec/*_spec.rb`` will be run against
every instance.

Tests located in ``spec/hosts/<hostname>/*_spec.rb`` will be run against
the specific instance with the given hostname.

Tests located in ``spec/groups/<groupname>/*_spec.rb`` will be run
against the instances in the given group.

Please note, this behavior only pertains to inventory generated by
Molecule. Specifying outside inventory files or scripts will disable
this functionality.

.. _`Ansible`: https://docs.ansible.com
.. _`Vagrant`: http://docs.vagrantup.com/v2
.. _`Serverspec`: http://serverspec.org
.. _`Testinfra`: http://testinfra.readthedocs.org
.. _`Rake`: https://github.com/ruby/rake
.. _`Rubocop`: https://github.com/bbatsov/rubocop
.. _`development`: http://pythonhosted.org/setuptools/setuptools.html#development-mode
.. _`pip pattern`: http://python-packaging-user-guide.readthedocs.org/en/latest/distributing/#working-in-development-mode
.. _`Travis`: https://travis-ci.org/
