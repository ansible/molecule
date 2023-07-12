# Molecule Next

Molecule "next" is the future major version of molecule, one that is currently
available from the main branch. One of the main goals of the new version is to
reduce the amount of magic and just rely on ansible core features.

# Implemented changes

- `roles-path` and `collections-paths` are no longer configurable for
  dependencies. Users are expected to make use of `ansible.cfg` file to
  alter them when needed.
- testinfra verifier driver was removed but current users should be able to
  keep calling their testinfra tests by using `command` or `shell` ansible
  modules from within `verify.yml` playbook.

# Planned changes

- Removal of provisioning drivers support and documenting, with examples, how to easily migrate to a self-provisioning approach.
- Refactoring how dependencies are installed
- Bringing ephemeral directory under scenario folder instead of the current
  inconvenient location under `~/.cache/molecule/...`
- Addition of a minimal `ansible.cfg` file under scenario folder that can
  be used to tell ansible from where to load testing content. This is to replace
  current Molecule magic around roles, collections and library paths and
  test inventory location. Once done you will be able to run molecule playbooks with ansible directly without
  having to define these folders.
