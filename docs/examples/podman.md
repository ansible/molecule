# Using podman containers

Below you can see a scenario that is using podman containers as test hosts.
When you run `molecule test --scenario-name podman` the `create`, `converge` and
`destroy` steps will be run one after another.

This example is using Ansible playbooks and it does not need any molecule
plugins to run. You can fully control which test requirements you need to be
installed.

## Config playbook

```yaml title="molecule.yml"
{!../molecule/podman/molecule.yml!}
```

```yaml title="requirements.yml"
{!../molecule/podman/requirements.yml!}
```

## Create playbook

```yaml title="create.yml"
{!../molecule/podman/create.yml!}
```

```yaml title="tasks/create-fail.yml"
{!../molecule/podman/tasks/create-fail.yml!}
```

## Converge playbook

```yaml title="converge.yml"
{!../molecule/podman/converge.yml!}
```

## Destroy playbook

```yaml title="destroy.yml"
{!../molecule/podman/destroy.yml!}
```
