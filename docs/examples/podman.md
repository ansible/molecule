# Using podman containers

Below you can see a scenario that is using podman containers as test hosts.
When you run `molecule test --scenario-name podman` the `create`, `converge` and
`destroy` steps will be run one after another.

This example is using Ansible playbooks and it does not need any molecule
plugins to run. You can fully control which test requirements you need to be
installed.

## Config playbook

```yaml title="molecule.yml"
{!podman/molecule.yml!}
```

```yaml title="requirements.yml"
{!podman/requirements.yml!}
```

## Create playbook

```yaml title="create.yml"
{!podman/create.yml!}
```

```yaml title="tasks/create-fail.yml"
{!podman/tasks/create-fail.yml!}
```

## Converge playbook

```yaml title="converge.yml"
{!podman/converge.yml!}
```

## Destroy playbook

```yaml title="destroy.yml"
{!podman/destroy.yml!}
```
