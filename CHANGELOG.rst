*******
History
*******

1.11.5
======

* Set ssh key if specified with the OpenStack driver.
* Pass ANSIBLE_CONFIG when executing ansible-lint

1.11.4
======

* Hide ansible-lint stacktrace on ``molecule verify``.
* Corrected linked clone platform options checking.

1.11.3
======

* Allow ``molecule status`` to handle the case where a container is stopped
  outside of molecule.

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
