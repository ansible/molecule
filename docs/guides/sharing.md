## Sharing Across Scenarios

Playbooks and tests can be shared across scenarios.

```bash
$ tree shared-tests
shared-tests
├── molecule
│   ├── centos
│   │   └── molecule.yml
│   ├── resources
│   │   ├── playbooks
│   │   │   ├── Dockerfile.j2 (optional)
│   │   │   ├── create.yml
│   │   │   ├── destroy.yml
│   │   │   ├── converge.yml  # <-- previously called playbook.yml
│   │   │   └── prepare.yml
│   │   └── tests
│   │       └── test_default.py
│   ├── ubuntu
│   │   └── molecule.yml
│   └── ubuntu-upstart
│       └── molecule.yml
```

Tests and playbooks can be shared across scenarios.

In this example the `tests` directory lives in a shared
location and `molecule.yml` points to the shared tests.

```yaml
verifier:
  name: testinfra
  directory: ../resources/tests/
```

In this second example the actions `create`,
`destroy`, `converge` and `prepare`
are loaded from a shared directory.

```yaml
provisioner:
  name: ansible
  playbooks:
    create: ../resources/playbooks/create.yml
    destroy: ../resources/playbooks/destroy.yml
    converge: ../resources/playbooks/converge.yml
    prepare: ../resources/playbooks/prepare.yml
```

## Shared Inventory

When using the `--shared-inventory` option, Molecule can share inventory data between scenarios.
This is useful when testing multiple scenarios that need to interact with the same set of instances.

The `molecule_shared_inventory_dir` variable is available in playbooks to access the shared inventory location:

```yaml
- name: Build shared inventory with INI template
  ansible.builtin.copy:
    content: "{{ inventory_ini }}"
    dest: "{{ molecule_shared_inventory_dir }}/shared_inventory.ini"
    mode: "0600"
  when: molecule_shared_inventory_dir != ""
  vars:
    inventory_ini: |
      [molecule]
      {% for platform in molecule_yml.platforms %}
      {{ platform.name }}{% for key, value in platform.get('host_vars', {}).items() %} {{ key }}={{ value }}{% endfor %}
      {% endfor %}

      [molecule:vars]
      ansible_user=root
      ansible_connection=docker
     delegate_to: localhost

- name: Force inventory refresh
  ansible.builtin.meta: refresh_inventory
```

The variable contains the path to the shared inventory directory when `--shared-inventory` is enabled,
or an empty string when running in normal mode or with `--parallel`.
