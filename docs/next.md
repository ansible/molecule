# Molecule Next

Molecule "next" is the future major version of molecule, one that is currently
available from the main branch. One of the main goals of the new version is to
reduce the amount of magic and just rely on ansible core features.

# Implemented changes

- `roles-path` and `collections-paths` are no longer configurable for
  dependencies. Users are expected to make use of [ansible.cfg](https://docs.ansible.com/ansible/latest/reference_appendices/config.html) file to
  alter them when needed.

- `molecule init` command is now only available to create a scenario
  using `molecule init scenario`.
  Users will no longer be able to create a role.
  Instead, users can make use of [ansible-galaxy](https://docs.ansible.com/ansible/latest/galaxy/dev_guide.html) to create a collection or role.

- From v6, `testinfra` is now an optional dependency.
  It will be removed in the next major release(v7).

# Planned changes

- Refactoring how dependencies are installed
- Bringing ephemeral directory under scenario folder instead of the current
  inconvenient location under `~/.cache/molecule/...`
- Addition of a minimal `ansible.cfg` file under the scenario folder that can
  be used to tell Ansible from where to load testing content. This is to replace
  current Molecule magic around roles, collections and library paths and
  test inventory location. Once done you will be able to run molecule playbooks with Ansible directly without
  having to define these folders.
