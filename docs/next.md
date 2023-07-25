# Molecule Next

Molecule "next" is the future major version of molecule, one that is currently
available from the main branch. One of the main goals of the new version is to
reduce the amount of magic and just rely on ansible core features.

# Implemented changes

- `roles-path` and `collections-paths` are no longer configurable for
  dependencies. Users are expected to make use of `ansible.cfg` file to
  alter them when needed.

# Planned changes

- Removal of provisioning drivers support and documenting, with examples, how to easily migrate to a self-provisioning approach.
- Removal of testinfra verifier driver and documenting how to call testinfra from inside the converge playbook to keep using the tool.
- Refactoring how dependencies are installed
- Bringing ephemeral directory under scenario folder instead of the current
  inconvenient location under `~/.cache/molecule/...`
- Addition of a minimal `ansible.cfg` file under scenario folder that can
  be used to tell ansible from where to load testing content. This is to replace
  current Molecule magic around roles, collections and library paths and
  test inventory location. Once done you will be able to run molecule playbooks with ansible directly without
  having to define these folders.
