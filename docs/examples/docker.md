# Using docker containers

Below you can see a scenario that is using docker containers as test hosts.
When you run `molecule test --scenario-name docker` the `create`, `converge` and
`destroy` steps will be run one after another.

This example is using Ansible playbooks and it does not need any molecule
plugins to run. You can fully control which test requirements you need to be
installed.

## Config playbook

```yaml title="molecule.yml"
{!tests/fixtures/integration/test_command/molecule/docker/molecule.yml!}
```

```yaml title="requirements.yml"
{!tests/fixtures/integration/test_command/molecule/docker/requirements.yml!}
```

## Create playbook

```yaml title="create.yml"
{!tests/fixtures/integration/test_command/molecule/docker/create.yml!}
```

```yaml title="tasks/create-fail.yml"
{!tests/fixtures/integration/test_command/molecule/docker/tasks/create-fail.yml!}
```

## Converge playbook

```yaml title="converge.yml"
{!tests/fixtures/integration/test_command/molecule/docker/converge.yml!}
```

## Destroy playbook

```yaml title="destroy.yml"
{!tests/fixtures/integration/test_command/molecule/docker/destroy.yml!}
```
