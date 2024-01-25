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
