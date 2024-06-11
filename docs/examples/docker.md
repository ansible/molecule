# Using docker containers

Below you can see a scenario that is using docker containers as test hosts.
When you run `molecule test --scenario-name docker` the `create`, `converge` and
`destroy` steps will be run one after another.

This example is using Ansible playbooks and it does not need any molecule
plugins to run. You can fully control which test requirements you need to be
installed.

## Config playbook

```yaml title="molecule.yml"
{!docker/molecule.yml!}
```

```yaml title="requirements.yml"
{!docker/requirements.yml!}
```

## Create playbook

```yaml title="create.yml"
{!docker/create.yml!}
```

```yaml title="tasks/create-fail.yml"
{!docker/tasks/create-fail.yml!}
```

## Converge playbook

```yaml title="converge.yml"
{!docker/converge.yml!}
```

## Destroy playbook

```yaml title="destroy.yml"
{!docker/destroy.yml!}
```
