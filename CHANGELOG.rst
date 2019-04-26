*******
History
*******

Unreleased
==========

* `dependency` step is now run by default before any playbook sequence step, including
  `create` and `destroy`. This allows the use of roles in all sequence step playbooks.
* Removed validation regex for docker registry passwords, all ``string`` values are now valid.
* Add ``tty`` option to the Docker driver.

2.20
====

Important Changes
-----------------

* Project now maintained by the Ansible Team, see `Move to Red Hat`_ for details
* Docker Container now hosted on `quay.io`_

.. _`Move to Red Hat`: https://molecule.readthedocs.io/en/latest/contributing.html#move-to-red-hat
.. _`quay.io`: https://quay.io/repository/ansible/molecule

Other
-----

* Molecule docker images will use the following convention on tags going forwards:

  * ``latest``: corresponds to the master branch, which should be viewed as unstable
  * ``2.20``: Git based tags
  * ``2.20a1``: pre-releases tags

* Molecule docker image no longer requires ``sudo`` when invoking ``molecule``.
* Molecule docker image no longer specifies ``USER molecule``.
* Officially advertise support for Python 3.5.
* Remove mandatory ``-r`` option for ``molecule init scenario``.
* Make the default scenario use the parent folder.
* Fix support for honouring environment variables such as ``MOLECULE_DEBUG``.
* Allow to customise the location of the ``Dockerfile.j2`` with the ``dockerfile`` option for the Docker driver.
* Add integer type coercion for the ``exposed_ports`` platform option.
* Add support for honouring ``PY_COLORS`` environment variable.
* Disable YAML lint truthy rule by default.
* Add validation for non-unique platform instance names.
* Add 'Getting Started' guide to the documentation for the benefit of new users.
* Allow to specify extra inventory sources not created by Molecule.
* Avoid including assets in the package ``sdist``.
* Add ``openssh-client`` to the Molecule Docker image.
* Fix ``ca-certificates`` installation for OpenSUSE.
* Add ``purge_networks`` option to the Docker driver.
* Add ``pid_mode`` option to the Docker driver.
* Constrain ``ansible-lint`` to ``>=4.0.2,<5``.
* Add the Linode driver (API v3).
* Provide documented example for using ``systemd`` enabled Docker images.
* Add ``winrm`` connection support for the delegated driver.
* Remove usage of ``sudo pip ..`` in driver installation documentation.
* Add ``override_command`` option to the Docker driver for overriding ``CMD`` directives.
* Only recommend to install ``'molecule[docker]'`` in the ``INSTALL.rst`` for the Docker driver.
* Sort scenario execution order by directory name.
* Fix Python package install for Docker ``prepare.yml`` on Fedora Rawhide.
* Update SHA-256 hash for the Goss binary.
* Remove ``Detox`` (deprecated) configuration example from ``Tox`` documentation.
* Add ``CODE_OF_CONDUCT.md``.
* Add optional ``cleanup`` sequence step.
* Allow to customise configuration file location with ``MOLECULE_GLOB`` environment variable.
* Molecule can now be called as a Python module (``python -m molecule``). Patch by `@ssbarnea`_.
* Add `Travis CI integration`_ and fix related test issues.
* Add Docker ``buildargs`` option for configuring the ``docker_image`` ``create.yml`` build step.

.. _`@ssbarnea`: https://github.com/ssbarnea
.. _`Travis CI integration`: https://travis-ci.com/ansible/molecule

2.19
====

* Bumped testinfra to 1.16.0 due to testinfra bug.
* Allows lowercase environment variables in the Docker scheme.
* Removes local mode from LXD documentation.

Important Changes
-----------------

Last release by :gh:`@retr0h <retr0h>`.  Subsequent releases will be made by
the Ansible team.

2.18.1
======

* Fixes #1484 - add ruby-etc apk package.
* Fix documentation of scenario sequences.

2.18
====

* Bump Goss to v0.3.6.
* Fixes docs build, appends #egg to tox-tags url.
* Fixes typo in base.py status docstring.
* Adds to goss docs about linting.
* Deprecated ansible 2.2 and 2.3 tests.
* Bumped ansible versions to test.
* Docs: Recommend prepare playbook for node setup.
* Updates typo in docker section of test_platforms_section.py.
* Adds install instructions for RuboCop.
* Updates tox-tags url in test-requirements.txt.
* Add support of restart_policy and restart_retries to docker driver.
* Added TERM=xterm to docker instance env.
* Added network_mode option to Docker container.
* Adds pre_build_image option to Docker create playbook.
* Remove the double `init` in the doc.
* Expand LXD driver functionality.
* Fixed the matrix subcommand yet again.

2.17
====

* Correct .env file interpolation.
* Fixes Tox link in docs.
* Adds tox-tags to test-requirements.txt.
* Expose config.project_directory as env var.
* Update Matrix usage.rst.
* Update ci.rst with Jenkinsfile example.
* Support passing arbitrary keys to vm.network.
* Pin wheel version to 0.30.0.
* Add git to docker DIND container.
* Added inspec download for Ubuntu 14.04.
* Added env to docker.
* Accept a single option to the matrix subcommand.
* Knob to change Ansible `no_log`.
* Bumped testinfra to 1.14.1 due to testinfra bug.
* Remove upgrade from Dockerfile.
* Bumped requirements.txt.
* Corrected provider_override_args.
* Add docker python and rubocop dependencies.
* Added python 3.7 support.

2.16
====

* Add feature for auto bumping docker image tag.
* Fixed Docker provider not using DOCKER_HOST environmental variable.
* Updates to the Ansible provisioning playbook for docker and vagrant for
  missing options.
* Documentation : dependencies on centos and docker driver clarifications.
* Added matrix subcommand.
* added pull: yes|no param to Docker executor.
* Added Gitlab CI example.
* Add information about the action which failed.
* Support Ansible 2.6.
* Corrected schema due to #1344.
* Prevalidator should enforce allowed options.
* Add support for multiple distributions to inspec verifier.
* Update InSpec to version 2.2.20.
* Update ansible-lint to version 3.4.23.
* Create unique keypair to allow parallel executions with OpenStack driver.
* Requirements update.
* Update the Dockerfile for work with az client and rubocop.

2.15
====

* Removed docker credential regexp validation.
* Added rsync to Docker image.
* Docker create playbooks: add tmpfs & security_opts docker_container
  parameters.
* Moved default scenario to a const.
* Pre-validate Molecule special variables.
* Added env file.
* Corrected command syntax.
* Delegated driver acts as managed.

2.14
====

* Add pre-validation.
* ``MOLECULE_`` special variables available in molecule.yml.
* Log Vagrant stdout to a file in MOLECULE_EPHEMERAL_DIRECTORY.
* Reintroduce base config merging.
* Corrected unit tests to work with tox.
* Add verifier mutually exclusive checking.
* UTF-8 issue in idempotence.
* Made prepare playbook optional.
* Bundle common playbooks.
* Added Goss linter.
* Disallow verifier.options with Goss and Inspec.

Important Changes
-----------------

* ``MOLECULE_`` special variables available in molecule.yml.
* Molecule introduces a new CLI option `--base-config`, which is
  loaded prior to each scenario's `molecule.yml`.  This allows
  developers to specify a base config, to help reduce repetition
  in their molecule.yml files.  The default base config is
  ~/.config/molecule/config.yml.
* Prepare playbook no longer needs to exist, unless using it.
* Molecule bundles Docker and Vagrant create/destroy playbooks.

2.13.1
======

* Enable Ansible 2.4 support with py36.

2.13
====

* Allow the destroying of remote libvirt instances.
* Bumped testinfra version for Ansible 2.5.1 compatibility.
* Added RuboCop as Inspec's linter.
* Minor fixes to Goss verifier playbook.
* Update documentation for verify and idempotency checks.
* Added Inspec verifier.
* Support Void Linux when using Docker driver.
* Converge with built in Molecule skip tags.
* Render inventory links relative to scenario dir.
* Disallow null provider.env values.
* Log vagrant errors.
* Enable py36 support for Ansible 2.5.
* Retry downloading goss 3 times.
* Delegated driver should report unknown on `molecule list`.
* Correct Docker container terminal sizing.
* Bumped Ansible 2.4 minor version in tox.
* Add docker_host attribute to templates to allow talking to a remote
  docker daemon.
* Across-the-board requirements update.
* Add parameter for Vagrant provider override.
* Add 'halt' option to Vagrant module.

Important Changes
-----------------

* Python 3.6 support.
* Added Inspec verifier.
* Added RuboCop linter for Inspec.

Breaking Changes
----------------

* Render inventory links relative to scenario dir instead of ephemeral dir.
  Unfortunately, this was a side effect of #1218.

2.12.1
======

* Disable pytest caching plugin.

Important Changes
-----------------

* No longer need to `.gitignore` the `.pytest_cache/` directory.

2.12
====

* Ensure prune properly removes empty dirs.
* Allow verify playbook to be shared.
* Added cookiecutter tests.
* Moved temporary files to $TMPDIR.
* Added and tested Ansible 2.5 support.
* Remove include tasks from driver playbooks.
* Set `delete_fip = yes` for os_server resources.
* Relaxed schema validation for which allows unknown keys in `molecule.yml`.
* Corrected AnsibleLint `-x` example.
* Added dind support and docs.
* Exclude .venv directory from yamllint.
* Move Molecule playbook vars into host inventory.
* Switch functional tests to pytest.raises.

Important Changes
-----------------

* Molecule writes temporary files to `$TMPDIR` hashed as
  `molecule/$role_name/$scenario_name/`.  Temporary files are no longer
  written to `$scenario_directory/.molecule/`.
* No longer need to `.gitignore` the `.molecule/` directory.

Breaking Changes
----------------

* Users of the Goss verifier will need to change their `verifier.yml` playbook
  to `verify.yml`.

2.11
====

* Correct verbose flag options with `--debug`.
* Bumped Ansible 2.4 and 2.3 minor versions.
* Reimplemented schema validation with Cerberus.
* Bumped version of jinja2.
* Move merge_dicts into util.
* Forward port Molecule v1 shell dependency manager.
* Vagrantfile cleanup.
* Ability to log into a Docker registry.

Important Changes
-----------------

* Reimplemented schema validation with Cerberus.  The Molecule file is
  thoroughly validated.  This may result in validation errors if the
  developer's `molecule.yml` is doing something unusual.

* Cleaned up the Vagrantfile, and allow the developer to change options
  on the base Vagrant config object.

Breaking Changes
----------------

* Changed Vagrant's `molecule.yml` `raw_config_args` to
  `provider_raw_config_args` for differentiating
  `instance_raw_config_args`.

2.10.1
======

* Correct Vagrant to automatically insert a keypair.
* Corrected synced_folders usage.

2.10
====

* Properly skipping Vagrant speedup keys in provider.
* Allow Vagrant to automatically insert a keypair.
* Correct molecule_vagrant.py bug where `provider_options`
  would cause Vagrant to fail if keys from #1147 were provided.
* Fix line length in cookie cutter README.

Important Changes
-----------------

* PR #1147 reduced Vagrant create time, which disabled Vagrant from
  automatically inserting a keypair.  Molecule's default is now changed
  back to Vagrant's default of True, which may reduce the speed of Vagrant
  create as fixed by #1147.

2.9
===

* Bumped yamllint version.
* Namespaced Docker registry.
* Reduce create time with Vagrant driver.
* Replace >>> with $ in documentation.
* Moved prune to run after destroy.
* Fix confusion between exposed and published ports in docker create
  playbook.
* Add basic support for libvirt in Vagrant driver.
* Ignore psutil on cygwin platform.
* Corrected ability to set multiple x options in provisioner's lint.
* Disallow privilege_escalation via schema.
* Validate schema for invalid ansible config options.
* Adding provision option for Vagrant driver.

Important Changes
-----------------

* These changes do not impact existing projects.  However, if one was using the
  old syntax, and upgraded create.yml, changes would be required.  The Docker
  driver's registry has been moved to a key named `url` under `registry`.

.. code-block:: yaml

    driver:
      name: docker
    platforms:
      - name: instance
        image: image_name:tag
        registry:
          url: registry.example.com

* Fix confusion between exposed and published ports in docker create playbook.

.. code-block:: yaml

    driver:
      name: docker
    platforms:
      - name: instance
        image: image_name:tag
        exposed_ports:
          - "53/udp"
          - "53/tcp"
        published_ports:
          - "0.0.0.0:8053:53/udp"
          - "0.0.0.0:8053:53/tcp"

2.8.2
=====

* Corrected ansible args.

2.8.1
=====

* Reverted, release does not exist.

2.8
===

* Improved quickstart video.
* Ability to specify a custom registry to Docker driver.
* Add a link to talk demo.
* Corrected incorreclty fixed bug when tags provided to provisioner.
* Corrected dependency scenario functional tests.
* Corrected incorrectly fixed bug when providing provisioner lint options.
* Regexp support in additional_files_or_dirs.
* Add custom nameserver to Docker container.
* Add network create and destroy support to Docker driver.

Breaking Changes
----------------

* The verifier's `additional_files_or_dirs` option is relative to the
  test directory, as opposed to the scenario directory.
* The verifier's `additional_files_or_dirs` option now supports regexp.
  Molecule will add additional files or directories, only when the glob
  succeeds.  Directories must be appended with the regexp to match, further
  details in the verifier's documentation.

2.7
===

* Ability to set a ulimit for the Docker driver.
* Switching log_driver from none to json-file to for compatibility with
  Ansible 2.2.
* Default to always destroy strategy.
* Support linked_clone for Vagrant 2.X.
* Bump tree-format to 0.1.2.
* Correct starting container on Docker edge by changing log_driver to none.
* Make psutil installation platform-dependent.

2.6
===

* Path searching to check ephemeral dir first.
* Update Goss verifier.yml.
* Bump ansible-lint version.
* Added example for setting Vagrant proxy settings for Linux.
* Never destroy instances if --destroy-never requested.
* Variable Molecule Ephemeral Directory.
* Added systemd example.

2.5
===

* Ignore provisioner.options when in the create/destroy provisioner.
* Switched Docker driver to a portable default command.
* Parallel instance management.
* Added Azure driver.
* Corrected testinfra SystemInfo tests.
* Execute `dependency` on check and converge sequence.
* Updated Docs usage of dependency role-file instead of requirements_file.
* Cleaned up YAML syntax.
* Execute linting first in test sequence.
* Support expose_ports option in docker driver.

2.4
===

* Corrected missing code block inside documentation.
* Bump ansible-lint version.
* Added yamlint to init scenario.
* Correct env path qualification.
* Add sudo package to Fedora section of Dockerfile template.
* Correct ANSIBLE_ROLES_PATH path component.
* Allow re-run of prepare playbook.

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
* Roles are linted with :gh:`Yamllint <adrienverge/yamllint>` vs v1's custom linter.

.. _`GCE Driver`: https://molecule.readthedocs.io/en/latest/configuration.html#gce
.. _`EC2 Driver`: https://molecule.readthedocs.io/en/latest/configuration.html#ec2
.. _`Goss Verifier`: https://molecule.readthedocs.io/en/latest/configuration.html#goss
.. _`LXC Driver`: https://molecule.readthedocs.io/en/latest/configuration.html#lxc
.. _`LXD Driver`: https://molecule.readthedocs.io/en/latest/configuration.html#lxd
.. _`OpenStack Driver`: https://molecule.readthedocs.io/en/latest/configuration.html#openstack
.. _`Porting Guide`: https://molecule.readthedocs.io/en/latest/porting.html
.. _`Scenarios`: https://molecule.readthedocs.io/en/latest/configuration.html#scenario
.. _`Delegated Driver`: https://molecule.readthedocs.io/en/latest/configuration.html#delegated

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

.. _`vars usage`: https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#defining-variables-in-a-playbook

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
  described in :pr:`398`.

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
* Running testinfra tests in parallel is no longer the default behaviour.

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
* Refactored commands.py to be more conducive to dispatch from DocOpt (:issue:`76`).
* Fixed :issue:`82` where callback plugin path wasn't being properly merged with
  user-defined values.
* Fixed :issue:`84` where ``molecule init`` would produce a molecule.yml that
  contained trailing whitespace.
* Fixed :issue:`85` preventing user-defined serverspec directory from being used.

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
* Leveraged new config flexibility to clean up old hack for ``molecule init``.
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
