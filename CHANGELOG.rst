*******
History
*******

Molecule follows `Semantic Versioning`_.  Therefore versioning will be much
different than previous versions of Molecule.

It will be safe to pin to MINOR versions of Molecule.  MINOR will add
functionality in a backwards-compatible manner.

.. _`Semantic Versioning`: http://semver.org

2.3
===

* Report friendly error message when interpolation fails.
* Added a new line after printing matrix.
* Added molecule header to generated Dockerfiles.
* Check supported python and ansible versions when executing Molecule.
* Sanitize user provided config options.
* Sanitize user provided env options.
* Added shell friendly env output

2.2.1
=====

* Ensure setup is run for prepare to correct ssh connection failures.

2.2
===

* Ability to execute a prepare playbook post create.
* Log deprecation warning when missing prepare.yml.
* Support Ansible 2.4.
* Revert "Add support import data from original ansible.cfg".
* Changed testinfra command to py.test.

2.1
===

* Add a destroy strategy to the `test` action.
* Delegated driver may or may not manage instances.

2.0.4
=====

* Fix Dockerfile for Fedora.

2.0.3
=====

* Generate host/group vars when host vars missing.

2.0.2
=====

* Pass the provisioner's env to the verifier.

2.0.1
=====

* Corrected init scenario validation.

2.0
===

* Major overhaul of Molecule.

Important Changes
-----------------

* Ansible playbooks to manage instances.
* Vagrant is managed through a custom Ansible module bundled with Molecule.
* Addition of `Scenarios`_.
* Addition of a `Delegated Driver`_ to test instances managed outside of
  Molecule.
* Promoted `Goss Verifier`_ to a supported verifier.
* Added `GCE Driver`_, `EC2 Driver`_, `LXC Driver`_, `LXD Driver`_ , and
  `OpenStack Driver`_ native Molecule drivers.

Breaking Changes
----------------

* Not compatible with Molecule v1 style config.
* Demoted serverspec support entirely.
* Does not support all of the Molecule v1 functionality or flexibility, in
  favor of simplicity and consistency throughout.
* Ansible 2.2 and 2.3 support only.
* See Molecule v1 to v2 `Porting Guide`_.
* Molecule no longer defaults to passing the `--become` flag to the
  `ansible-playbook` command.
* Roles are linted with `Yamllint`_ vs v1's custom linter.

.. _`GCE Driver`: http://molecule.readthedocs.io/en/latest/configuration.html#gce
.. _`EC2 Driver`: http://molecule.readthedocs.io/en/latest/configuration.html#ec2
.. _`Goss Verifier`: http://molecule.readthedocs.io/en/latest/configuration.html#goss
.. _`LXC Driver`: http://molecule.readthedocs.io/en/latest/configuration.html#lxc
.. _`LXD Driver`: http://molecule.readthedocs.io/en/latest/configuration.html#lxd
.. _`OpenStack Driver`: http://molecule.readthedocs.io/en/latest/configuration.html#openstack
.. _`Porting Guide`: http://molecule.readthedocs.io/en/latest/porting.html
.. _`Scenarios`: http://molecule.readthedocs.io/en/latest/configuration.html#scenario
.. _`Delegated Driver`: http://molecule.readthedocs.io/en/latest/configuration.html#delegated
.. _`Yamllint`: https://github.com/adrienverge/yamllint

1.25.1
======

* Update ansible-lint for Ansible 2.4 compatibility.

1.25
====

* Display output when `idempotence` fails.
* Changed basebox to ubuntu/trusty64 for molecule init.
* Allow disable_cache parameter for Docker containers enhancement.
* Update goss verifier.
* Add a 'private' parameter in OpenStack driver.

1.24
====

* Support Ansible 2.3.

1.23.3
======

* Clean up {group,host}_vars on destroy.

1.23.2
======

* Globally disable cowsay, since it impacts the idempotence check.

1.23.1
======

* Added ungrouped hosts under all.

1.23
====

* Prescriptive ansible.cfg defaults.
* Ansible v2 has deprecated ansible_ssh_{host,port,user}.
* Docker driver: use POSIX shell and support more linux package systems.
* Add quotes around ansible_ssh_private_key_file format.
* Ansible 1.9 No longer supported.

1.22
====

* Handling of networks with Docker driver.

1.21.1
======

* Corrected None RepoTags bug with docker driver.

1.21
====

* No longer skip setting hostname with Vagrant's libvirt provider.
* Openstack: Allow using ssh keys from ssh-agent.
* Obtain driver from state file if set.
* Updated to Goss 0.3.0.
* Remove terminal warnings while running apt.
* Support for new docker sdk.
* Updated doc for docker driver links.

Breaking Changes
----------------

* The `docker-py` pip package has been deprecated in favor of `docker`.

1.20.3
======

* Version bump, network interuption while uploading package to pypi.

1.20.2
======

* Correct testinfra tests discovered twice.

1.20.1
======

* Correct too many authentication failures error.

1.20
====

* Expose network configuration to docker driver.
* Openstack: Performance improvements for multiinstance setups.
* Do not require a project_config when a local_config is present.
* Corrected molecule.yml's group_vars/host_vars.

Breaking Changes
----------------

* The `host_vars` and `group_vars` section of molecule.yml no longer accepts a
  list, rather a dict similar to Ansible's `vars usage`_.

.. _`vars usage`: http://docs.ansible.com/ansible/playbooks_variables.html#variables-defined-in-a-playbook

1.19.3
======

* Openstack: Use configured ssh key.

1.19.2
======

* Properly handle testinfra verbose flag setting.

1.19.1
======

* Add raw_config_args option to providers.

1.19
====

* Convert vagrantfile from relying on jinja.

1.18.1
======

* Make Openstack ssh timeout configurable.

1.18
====

* Fix availability timeout in Openstack driver.
* Do not alter users known_hosts file in Openstack driver.
* Allow using environment variables in molecule.ym.
* Make ansible.cfg settings configurable through molecule.yml.
* Add multiple network support in Openstack driver.
* Add links functionality to Docker driver.
* Switched options from 'sudo' to 'become'.

1.17.3
======

* Create test skeleton with `molecule init` when initializing a role in current
  directory.

1.17.2
======

* Fix unittests to allow ls to be in both /usr/bin and /bin.
* Force raw_env_vars to string for `ansible-playbook`.

1.17.1
======

* Correct functional tests.
* Correct locale issues with print class of methods.
* Correct ansible-lint exit error when role dependency is in newer dictionary
  format.
* Pass env to `ansible-lint`.

1.17
====

* Cleanup sphinx doc generation.
* Bumped testinfra requirement which drops the now useless installation of
  which in centos and fedora images.
* Made OpenStack's ip pool configurable.
* Corrected Docker's overlayfs for RPM based distros.
* Fixed OpenStack's security_groups default for newer shade versions.
* Added missing bash completion targets.

1.16.1
======

* Removed check mode from running in test cycle.

Breaking Changes
----------------

* Molecule no longer runs in "Dry Mode" as part of `molecule test`.  If one
  wishes to incorporate check as part of `test`, molecule.yml can be updated
  to include this as part of the test sequence.

1.16
====

* Slightly improved unit test coverage.
* Various doc improvements.
* Added Gilt usage to docs.
* Reimplemented info, error, debug message handling.
* Nice error message when rake and/or rubocop missing.
* Fix task determination on idempotence failure.
* Added a github issue template.
* Logging of dependency command execution.

1.15
====

* Added a shell dependency manager.
* Created a CI section to documentation with Tox details.
* Rename dependencies key to dependency.

Breaking Changes
----------------

* The galaxy override options have been moved to the `dependency` section of
  molecule's config.  No longer support a top level `dependencies` config key.
  This functionality was added in 1.14, and this follow-up corrects the usage,
  before 1.14 was utilized.

1.14.1
======

* Fix openstack driver login and ssh key generation.

1.14
====

* Made improvements to unit/functional tests.
* Fixed Goss verifier under Ansible 2.2.
* Removed testinfra config backward compatibility.
* Broke out role dependency into a subcommand.

Breaking Changes
----------------

* The testinfra override options have been moved to the `verifier` section of
  molecule's config.  No longer support a top level `testinfra` config key.
* The galaxy override options have been moved to the `dependencies` section of
  molecule's config.  No longer support a `galaxy` key inside the top level
  `ansible` section.

1.13
====

* Implement environment handling in docker driver.
* Added vmware_workstation provider to vagrant.
* Improved overall logging, including logging of `sh` commands when debug flag
  set.
* Avoid images with <none> tag.
* Support and test ansible 2.2 and 2.1.2.
* Allow nested testinfra test directory structure.
* Ability to pass arbitrary ansible cli flags to `converge`.
* Added IRC info to docs.
* Return exit code from goss verifier.
* General cleanup of modules and documentation.
* Bumped requirements versions.

1.12.6
======

* Disable diff when executing idempotent check.
* Make sure ansible-lint respects the molecule ignore_paths.
* Convert readthedocs links for their .org->.io migration for hosted projects.

1.12.5
======

* Increased test coverage.
* Allow group/host vars in molecule.yml to work with ansible 1.9.
* Pass HOME to ansible-lint environment.
* Expose driver to login.
* Improved login error message messaging.

1.12.4
======

* Added a private disabled top level key.  Do not use or rely on this key.
  Added for our molecule adoption.
* Added a coverage minimum.
* More unit and functional coverage.

1.12.3
======

* Write templates even when a custom ansible.cfg is specified.

1.12.2
======

* Removed default multiple-instances from init.

1.12.1
======

* Preserve ansible.cfg when supplying a custom one.

1.12
====

* Additional command tests.
* Changed connection to ansible_connection.
* Implemented click vs docopt.  This slightly changes the CLI's semantics.
* Removed the driver python packages from installing with molecule.
* Set ssh key if specified in OpenStack driver.
* Using py.test as functional test runner.
* Added a Gemfile to ``molecule init`` serverspec verifier.
* Added SUSE docker driver support.
* Display the list of non-idempotent tasks with ``molecule idempotence``.

Breaking Changes
----------------

* The ``--debug`` flag is no longer passed to the subcommand.  The command and
  subcommand args were getting munged together, and passed to the core.  They
  are now handled separately.
* Removed the ``--debug`` subcommand flag from all usage -- it was never used.
* The ``init`` subcommand requires an optional ``--role`` flag vs a role
  argument when naming the role to initialize.
* The ``init`` subcommand requires a ``--driver`` flag when creating a driver
  other than vagrant.
* The ``init`` subcommand requires a ``--verifier`` flag when creating a
  verifier other than testinfra.
* The ``login`` subcommand requires a ``--host`` flag when more than one
  instance exists.
* One must install the appropriate python package based on the driver used.

1.11.5
======

* Set ssh key if specified with the OpenStack driver.
* Pass ANSIBLE_CONFIG when executing ansible-lint.

1.11.4
======

* Hide ansible-lint stacktrace on ``molecule verify``.
* Corrected linked clone platform options checking.

1.11.3
======

* Handle when a container is stopped outside of molecule, when running
  ``molecule status``.

1.11.2
======

* Preserve sudo passed in verifier options.

1.11.1
======

* Corrected bug when passing the ``--platform`` flag.

1.11
====

* General cleanup of core module.
* Various documentation updates.
* Pull molecule status from state file when using Vagrant driver.
* Added alpha Goss verifier support.
* Updated runtime requirements to current versions.
* Implemented ``molecule check`` subcommand.
* Configure verifier to be test kitchen like.
* Ability to declare multiple drivers in config.
* Implement ansible groups inheritance.

Breaking Changes
----------------

Previously molecule would execute a test framework based on the existence of a
directory structure.  This is no longer the case.  Molecule will execute the
configured suite, where `testinfra` is the default.  See docs.

1.10.3
======

* Reimplemented idempotence handling. Removed the idempotence ansible callback
  plugin, in favor of a native implementation.

Note
----

There is no change in workflow.  Molecule still reports if a converge was
idempotent or not.  However, it no longer reports which task(s) are not
idempotent.

1.10.2
======

* Removed pytest-xdist from runtime deps.  This allows testinfra's dependency
  on pytest to properly install.

1.10.1
======

* Pinned to explicit version of testinfra, due to pytest incompatabilities.

1.10
====

* Added ability to specify custom dockerfile.
* Added ability to generate and destroy temporary openstack keypair and ssh key
  file if they are not specified in the molecule.yml.
* Implemented Cookiecutter for ``molecule init``.
* Documentation improvements.

Breaking Changes
----------------

Roles may fail to converge due to the introduction of additional verifiers.

* Added flake8 linter to testinfra verifier.
* Implemented ansible lint.

1.9.1
=====

* Correct a converge --debug bug.
* Correct ansible galaxy role path.

1.9
===

* Restructured and reogranized internal code, tests, and docs.
* Added functional scenario tests.
* Improved unit tests/coverage.
* Added auto docker api version recognition to prevent api mismatch errors.
* Added fallback status for vagrant driver.
* Control over ansible galaxy options.
* Display molecule status when not created.
* Added dependency installation state, and installation step for syntax check.
* Pinned runtime requirements.
* Update login to use state data.
* Ability to target ansible groups with testinfra.
* Ability to target docker hosts with serverspec.
* Added ../../ to rolepath to fix ansible 2.1.1 default role search.
* Added docker volume mounting.
* Add support for Docker port bindings.
* Implemented a new core config class.

Breaking Changes
----------------

* Existing Testinfra tests which use the Docker driver need updating as
  described in `398`_.

.. _`398`: https://github.com/metacloud/molecule/issues/398

1.8.4
=====

* Fixed role_path with ansible 2.1.1.

1.8.3
=====

* Fixed passing flags to molecule test.

1.8.2
=====

* Fixed a bad reference to the molecule_dir config variable.

1.8.1
=====

* Fixed a bug where molecule would fail if .molecule/ didn't already exist.

1.8
===

* Added native support for OpenStack provider.
* Fixed a bug where testinfra_dir config option wasn't being handled.
* Fixed a bug with ``molecule login`` where its host matching didn't work with
  overlapping names.

1.7
===

* It's now possible to define host_vars and group_vars in ansible section of
  molecule.yml.
* The --platform CLI option now supports ``all``.
* Corrected issue with specifying serverspec args in molecule.yml.

1.6.3
=====

* Updated config parsing so that testinfra.sudo and testinfra.debug can be set
  in molecule.yml.
* Demo role now pulls in correct serverspec config.

1.6.2
=====

* Added inventory-file flag to ``molecule check`` to address Ansible 1.9.x
  specific issue.

1.6.1
=====

* Fixed a bug preventing ``molecule test`` from working.
* Added a demo role for functional testing.

1.6
===

* Added --offline option to ``molecule init``.
* ``molecule status`` now shows hosts by default.
* ``molecule test`` will now fail immediately when encountering an error.
* Switched to Python's logging module for displaying STDOUT, STDERR.
* Added support for libvirt provider.
* Added ``molecule check`` to check playbook syntax.
* Testinfra parameters can now be set as vars in molecule.yml.
* Running testinfra tests in parallel is no longer the default behavior.

1.5.1
=====

* Fixed issue with testinfra and serverspec attempting to share args.
* Added --sudo option for testinfra.
* Added tab completion support.
* Misc. Docker updates and fixes.

1.5
===

* Added support for Docker provisioner.
* Added support for group_vars.

1.4.2
=====

* Made "append_platform_to_hostname" False by default.
* Testinfra tests now run in parallel.
* ``init`` now generates testinfra tests by default.
* Testinfra env vars (including ssh) are now consistent with what is passed to
  ansible-playbook.

1.4.1
=====

* Fixed a bug where testinfra_dir wasn't being used.
* Changed append_platform_to_hostname to default to False.

1.4
===

* Updated ``init`` to install role dependencies from Ansible Galaxy.
* Now using DocOpt subcommands to dispatch commands internally.
* Updated ``login`` command to take no hostname (for single instances) and
  partial hostnames.
* Improved visibility when running (and not running) tests.
* Can now pass multiple instances of --tags for specifying more than one tag.
* Can now pass --destroy flag to ``test`` with various options suitable for use
  in CI.
* Numerous small bug fixes.

1.3
===

* Added very basic support for the vagrant-triggers plugin.

1.2.4
=====

* Fixed a bug introduced in 1.2.3 preventing ``init`` from working.

1.2.3
=====

* Fixed a bug where ``destroy`` would fail on VMs that hadn't been created.
  Caused errors running ``test``.
* Moved rubocop, rake, and testinfra into validators. Added tests.
* Moved ansible-playbook logic out of core, commands and into a dedicated
  class. Added tests.
* Provisioner logic moved to its own class outside of core.

1.2.2
=====

* Added a CLI option for the ``list`` command to make the output machine
  readable.
* Refactored commands.py to be more conducive to dispatch from DocOpt (#76).
* Fixed issue #82 where callback plugin path wasn't being properly merged with
  user-defined values.
* Fixed issue #84 where ``molecule init`` would produce a molecule.yml that
  contained trailing whitespace.
* Fixed issue #85 preventing user-defined serverspec directory from being used.

1.2.1
=====

* Updated idempotence plugin path to be appended to existing plugin path rather
  than overwriting it.
* Fixed case where idempotence plugin would crash when unable to read response
  dictionary.

1.2
===

* Added support for Vagrant 1.8's linked_clone option.
* Updated idempotence test to use an Ansible callback plugin that will print
  failed tasks.
* Path to templates can now be relative to a user's home directory.
* box_url in Vagrantfile is no longer set if box_version is defined.
* Uses the latest version of python-vagrant.

1.1.3
=====

* Fixed a bug where inventory wasn't getting created on a new converge.
* Linting now targets a specific list of file extensions.
* Hostname created during ``init`` is now sanitized.
* Creattion of python cache directory is now disabled by default.

1.1.2
=====

* Fixed a bug where calling ``create`` separately from ``converge`` wasn't
  generating an inventory file.

1.1.1
=====

* Cleaned up state file management logic to be more concise, functional for
  other purposes.
* Removed --fast flag from converge in favor of using state file for fast
  converging.
* Instance hostname is now printed during serverspec runs.
* Fixed a bug where loading template files from absolute paths didn't work.

1.1
===

* Added support for static inventory where molecule can manage existing sites,
  not just vagrant instances.
* Added support for skipping instance/inventory creation during
  ``molecule converge`` by passing it --fast. MUCH faster.

1.0.6
=====

* Fixed a bug preventing vagrant raw_config_args from being written to
  vagrantfile template.
* Cleaned up error messaging when attempting to `molecule login` to a
  non-existent host.
* Added release engineering documentation.
* Moved commands into a separate module.
* Switched to using yaml.safe_load().
* Added more debugging output.

1.0.5
=====

* Added support for Vagrant box versioning. This allows teams to ensure all
  members are using the correct version in their development environments.

1.0.4
=====

* Fixed a bug where specifying an inventory script was causing molecule to
  create it.
* config_file and inventory_file specified in ansible block are now treated as
  overrides for molecule defaults.

1.0.3
=====

* Updated format of config.yml and molecule.yml so they use the same data
  structure for easier merging. In general it's more clear and easy to
  understand.
* Defaults are now loaded from a defaults file (YAML) rather than a giant hash.
  Maintaining data in two formats was getting tiresome.
* Decoupled main() from init() in Molecule core to make future tests easier.
* Removed mock from existing tests that no longer require it now that main() is
  decoupled.
* Moved all config handling to an external class. Greatly simplified all logic.
* Added tests for new config class.
* Cleaned up all messages using format() to have consistent syntax.
* Fixed status command to not fire unless a vagrantfile is present since it was
  triggering vagrant errors.
* Renamed _init_new_role() to init() to be consistent with other commands.
* Fixed incorrect messaging in _print_valid_providers().
* Fixed edge case in vagrantfile template to make sure we always have default
  cpus/memory set for virtualbox instances.
* Leveraged new config flexibility to clean up old hack for `molecule init`.
* Fixed utility test for deep_merge that was failing.
* Made print_line two different functions for stdout and stderr.
* Updated print functions to be Python 3 ready.
* Moved template creation into a generic function.
* Test all the (moved) things.
* Updated image assets.
* Removed aio/mcp naming from docs and templates.

1.0.2
=====

* Switched to deep merging of config dicts rather than using update().

1.0.1
=====

* Fixed trailing validator, and broke out into a module.

1.0
===

* Initial release.
