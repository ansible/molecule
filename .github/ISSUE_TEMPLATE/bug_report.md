---
name: Bug report
about: Please test the main branch before raising bugs.
labels: bug
---

<!--- Verify first that your issue is not already reported on GitHub -->
<!--- Do not report bugs before reproducing them with the code of the main branch! -->
<!--- Please also check https://ansible.readthedocs.io/projects/molecule/faq/ --->
<!--- Please use https://github.com/ansible-community/molecule/discussions for usage questions -->

# Issue Type

- Bug report

# Molecule and Ansible details

```
ansible --version && molecule --version
```

Molecule installation method (one of):

- source
- pip

Ansible installation method (one of):

- source
- pip
- OS package

Detail any linters or test runners used:

# Desired Behavior

Please give some details of the feature being requested or what
should happen if providing a bug report.

# Actual Behaviour

Please give some details of what is actually happening.
Include a [minimum complete verifiable example](https://stackoverflow.com/help/mcve) with
output of running `molecule --debug`.
