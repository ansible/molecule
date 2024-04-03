## Monolith Repo

Molecule is generally used to test playbooks or roles in isolation.
However, it can also test them from a monolith repo.

```bash
$ tree monolith-repo -L 3 --prune
monolith-repo
 ├── library
 │   └── foo.py
 ├── plugins
 │   └── filters
 │       └── foo.py
 └── roles
     ├── bar
     │   └── README.md
     ├── baz
     │   └── README.md
     └── foo
         └── README.md
```

The role initialized with Molecule (baz in this case) would simply
reference the dependent roles via its `converge.yml` or meta
dependencies.

Molecule can test complex scenarios leveraging this technique.

```bash
$ cd monolith-repo/roles/baz
$ molecule test
```

Molecule is simply setting the `ANSIBLE_*` environment variables. To
view the environment variables set during a Molecule operation pass the
`--debug` flag.

```bash
$ molecule --debug test

DEBUG: ANSIBLE ENVIRONMENT
---
ANSIBLE_CONFIG: /private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/ansible.cfg
ANSIBLE_FILTER_PLUGINS: /Users/jodewey/.pyenv/versions/2.7.13/lib/python2.7/site-packages/molecule/provisioner/ansible/plugins/filters:/private/tmp/monolith-repo/roles/baz/plugins/filters:/private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/plugins/filters
ANSIBLE_LIBRARY: /Users/jodewey/.pyenv/versions/2.7.13/lib/python2.7/site-packages/molecule/provisioner/ansible/plugins/libraries:/private/tmp/monolith-repo/roles/baz/library:/private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/library
ANSIBLE_ROLES_PATH: /private/tmp/monolith-repo/roles:/private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/roles
```

Molecule can be customized any number of ways. Updating the
provisioner's env section in `molecule.yml` to suit the needs of the
developer and layout of the project.

```yaml
provisioner:
  name: ansible
  env:
    ANSIBLE_$VAR: $VALUE
```
