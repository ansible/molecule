---
hide:
  - navigation
  - toc
---

# About Ansible Molecule

Molecule is an Ansible testing framework designed for developing and testing
[Ansible](https://ansible.com) collections, playbooks, and roles.

Molecule leverages standard Ansible features including inventory, playbooks,
and collections to provide flexible testing workflows. Test scenarios can
target any system or service reachable from Ansible, from containers and
virtual machines to cloud infrastructure, hyperscaler services, APIs,
databases, and network devices. Molecule can also validate inventory
configurations and dynamic inventory sources.

Molecule encourages an approach that results in consistently developed
Ansible content that is well-written, easily understood and maintained.

Molecule supports only the latest two major versions of Ansible (N/N-1).

Once installed, the command line can be called using any of the methods
below:

```bash
molecule ...
python3 -m molecule ...  # python module calling method
```

Molecule projects also hosts the [community.molecule] collection, which
contains some filters, plugins, roles and playbooks that can be used by
molecule test writers to ease writing tests.


