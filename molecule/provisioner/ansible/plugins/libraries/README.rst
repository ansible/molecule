Ansible Module overrides for Molecule
=====================================

Sometimes Molecule *itself* may need newer modules which are not available in current versions of Ansible.

Solution is to copy the new module here, add the `molecule_` prefix to the filename and
start using it with the same prefix.

There is no need to update module name in its source, ansible would rely on filename alone.

* molecule_docker_image.py : can be removed once ansible_min_version==2.9
