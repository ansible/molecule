CHANGELOG for molecule
======================
1.2.3
----

* Fixed a bug where ``destroy`` would fail on VMs that hadn't been created. Caused errors running ``test``.
* Moved rubocop, rake, and testinfra into validators. Added tests.
* Moved ansible-playbook logic out of core, commands and into a dedicated class. Added tests.
* Provisioner logic moved to its own class outside of core.

1.2.2
----

* Added a CLI option for the ``list`` command to make the output machine readable.
* Refactored commands.py to be more conducive to dispatch from DocOpt (#76).
* Fixed issue #82 where callback plugin path wasn't being properly merged with user-defined values.
* Fixed issue #84 where ``molecule init`` would produce a molecule.yml that contained trailing whitespace.
* Fixed issue #85 preventing user-defined serverspec directory from being used.

1.2.1
----

* Updated idempotence plugin path to be appended to existing plugin path rather than overwriting it.
* Fixed case where idempotence plugin would crash when unable to read response dictionary.

1.2.0
----

* Added support for Vagrant 1.8's linked_clone option.
* Updated idempotence test to use an Ansible callback plugin that will print failed tasks.
* Path to templates can now be relative to a user's home directory.
* box_url in Vagrantfile is no longer set if box_version is defined.
* Uses the latest version of python-vagrant.

1.1.3
----

* Fixed a bug where inventory wasn't getting created on a new converge.
* Linting now targets a specific list of file extensions.
* Hostname created during ``init`` is now sanitized.
* Creattion of python cache directory is now disabled by default.

1.1.2
----

* Fixed a bug where calling ``create`` separately from ``converge`` wasn't generating an inventory file.

1.1.1
----

* Cleaned up state file management logic to be more concise, functional for other purposes.
* Removed --fast flag from converge in favor of using state file for fast converging.
* Instance hostname is now printed during serverspec runs.
* Fixed a bug where loading template files from absolute paths didn't work.

1.1.0
----

* Added support for static inventory where molecule can manage existing sites, not just vagrant instances.
* Added support for skipping instance/inventory creation during ``molecule converge`` by passing it --fast. MUCH faster.

1.0.6
----

* Fixed a bug preventing vagrant raw_config_args from being written to vagrantfile template.
* Cleaned up error messaging when attempting to `molecule login` to a non-existent host.
* Added release engineering documentation.
* Moved commands into a separate module.
* Switched to using yaml.safe_load().
* Added more debugging output.

1.0.5
----

* Added support for Vagrant box versioning. This allows teams to ensure all members are using the correct version in their development environments.

1.0.4
----

* Fixed a bug where specifying an inventory script was causing molecule to create it.
* config_file and inventory_file specified in ansible block are now treated as overrides for molecule defaults.

1.0.3
----

* Updated format of config.yml and molecule.yml so they use the same data structure for easier merging. In general it's more clear and easy to understand.
* Defaults are now loaded from a defaults file (YAML) rather than a giant hash. Maintaining data in two formats was getting tiresome.
* Decoupled main() from init() in Molecule core to make future tests easier.
* Removed mock from existing tests that no longer require it now that main() is decoupled.
* Moved all config handling to an external class. Greatly simplified all logic.
* Added tests for new config class.
* Cleaned up all messages using format() to have consistent syntax.
* Fixed status command to not fire unless a vagrantfile is present since it was triggering vagrant errors.
* Renamed _init_new_role() to init() to be consistent with other commands.
* Fixed incorrect messaging in _print_valid_providers().
* Fixed edge case in vagrantfile template to make sure we always have default cpus/memory set for virtualbox instances.
* Leveraged new config flexibility to clean up old hack for `molecule init`.
* Fixed utility test for deep_merge that was failing.
* Made print_line two different functions for stdout and stderr.
* Updated print functions to be Python 3 ready.
* Moved template creation into a generic function.
* Test all the (moved) things.
* Updated image assets.
* Removed aio/mcp naming from docs and templates.

1.0.2
----

* Switched to deep merging of config dicts rather than using update().

1.0.1
----

* Fixed trailing validator, and broke out into a module.

1.0
-----

* Initial release.
