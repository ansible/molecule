.. image:: https://cloud.githubusercontent.com/assets/9895/11258895/12a1bb40-8e12-11e5-9adf-9a7aea1ddda9.png
   :alt: Molecule
   :width: 500
   :height: 132
   :align: center

Molecule
========

.. image:: https://badge.fury.io/py/molecule.svg
   :target: https://badge.fury.io/py/molecule
   :alt: PyPI Package

.. image:: https://readthedocs.org/projects/molecule/badge/?version=latest
   :target: https://molecule.readthedocs.org/en/latest/
   :alt: Documentation Status

.. image:: https://travis-ci.org/rgreinho/molecule.svg?branch=master
   :target: https://travis-ci.org/rgreinho/molecule
   :alt: Build Status

Molecule is designed to aid in the development and testing of
`Ansible`_ roles including support for multiple instances,
operating system distributions, virtualization providers and test frameworks.

It leverages `Vagrant`_ to manage virtual machines,
with support for multiple Vagrant providers (currently VirtualBox and OpenStack).
Molecule supports `Serverspec`_ or `Testinfra`_ to run tests.  Molecule uses an `Ansible`_
`playbook`_ (``playbook.yml``), to execute the `role`_ and its tests.

.. _`Ansible`: https://docs.ansible.com
.. _`Vagrant`: http://docs.vagrantup.com/v2
.. _`Test Kitchen`: http://kitchen.ci
.. _`playbook`: https://docs.ansible.com/ansible/playbooks.html
.. _`role`: http://docs.ansible.com/ansible/playbooks_roles.html
.. _`Serverspec`: http://serverspec.org
.. _`Testinfra`: http://testinfra.readthedocs.org

Quick Start
-----------

Install molecule using pip:

.. code-block:: bash

  $ pip install molecule

Create a new role:

.. code-block:: bash

  $ molecule init foo
  Successfully initialized new role in ./foo/

Update the role with needed functionality and tests.  Now test it:

.. code-block:: bash

  $ cd foo
  $ molecule test
  ==> vagrant-01: VM not created. Moving on...
  ==> vagrant-01: VM not created. Moving on...
  Bringing machine 'vagrant-01' up with 'virtualbox' provider...
  ==> vagrant-01: Importing base box 'hashicorp/precise64'...
  ...
  ==> vagrant-01: Machine not provisioned because `--no-provision` is specified.

  PLAY [all] ********************************************************************

  GATHERING FACTS ***************************************************************

  ok: [vagrant-01]

  TASK: [foo | install curl] ****************************************************

  changed: [vagrant-01]

  PLAY RECAP ********************************************************************
  vagrant-01                 : ok=2    changed=1    unreachable=0    failed=0

  Idempotence test in progress... OKAY
  Inspecting 2 files
  ..

  2 files inspected, no offenses detected
  /Users/jodewey/.rvm/rubies/ruby-2.2.0/bin/ruby -I/Users/jodewey/.rvm/gems/ruby-2.2.0/gems/rspec-support-3.3.0/lib:/Users/jodewey/.rvm/gems/ruby-2.2.0/gems/rspec-core-3.3.2/lib /Users/jodewey/.rvm/gems/ruby-2.2.0/gems/rspec-core-3.3.2/exe/rspec --pattern spec/\*_spec.rb,spec/vagrant-01/\*_spec.rb,spec/hosts/vagrant-01/\*_spec.rb,spec/group_1/\*_spec.rb,spec/groups/group_1/\*_spec.rb,spec/group_2/\*_spec.rb,spec/groups/group_2/\*_spec.rb

  Package Installation
    Package "curl"
      should be installed

  Finished in 0.40244 seconds (files took 0.90459 seconds to load)
  1 example, 0 failures

  ==> vagrant-01: Attempting graceful shutdown of VM...
  ==> vagrant-01: Destroying VM and associated drives...

Documentation
-------------

http://molecule.readthedocs.org/en/latest/

License
-------

MIT

The logo is licensed under the `Creative Commons NoDerivatives 4.0 License`_.  If you have some other use in mind, contact us.

.. _`Creative Commons NoDerivatives 4.0 License`: https://creativecommons.org/licenses/by-nd/4.0/
