# Contributing

- To see what's discussed see the [discussions
  ](https://github.com/ansible-community/molecule/discussions).
- Join the Molecule [community working
  group](https://github.com/ansible/community/wiki/molecule) if you
  would like to influence the direction of the project.
- Join us in `#ansible-devtools` on
  [libera.chat](https://web.libera.chat/?channel=#ansible-molecule) matrix/irc,
  or [molecule discussions](https://github.com/ansible-community/molecule/discussions).
- The full list of Ansible email lists and IRC channels can be found in
  the [communication
  page](https://docs.ansible.com/ansible/latest/community/communication.html).

## Guidelines

- We are interested in various different kinds of improvement for
  Molecule; please feel free to raise an
  [Issue](https://github.com/ansible-community/molecule/issues/new/choose)
  if you would like to work on something major to ensure efficient
  collaboration and avoid duplicate effort.
- Create a topic branch from where you want to base your work.
- Make sure you have added tests for your changes.
- Although not required, it is good to sign off commits using
  `git commit --signoff`, and agree that usage of `--signoff`
  constitutes agreement with the terms of [DCO
  1.1](https://github.com/ansible-community/molecule/blob/main/DCO_1_1.md).
- Run all the tests to ensure nothing else was accidentally broken.
- Reformat the code by following the formatting section below.
- Submit a pull request.

## Code Of Conduct

Please see our [Code of
Conduct](https://github.com/ansible-community/molecule/blob/main/.github/CODE_OF_CONDUCT.md)
document.

## Pull Request and Governance

- If your PRs get stuck [join us on
  IRC](https://github.com/ansible/community/wiki/Molecule#join-the-discussion)
  or add to the [working group
  agenda](https://github.com/ansible/community/wiki/Molecule#meetings).
- The code style is what is enforced by CI, everything else is
  off-topic.
- All PRs must be reviewed by one other person. This is enforced by
  GitHub. Larger changes require +2.

## Testing

Molecule has an extensive set of unit and functional tests. Molecule
uses [Tox](https://tox.wiki/en/latest/) factors to generate a
matrix of python x Ansible x unit/functional tests. Manual setup
required as of this time.

### Dependencies

Tests will be skipped when the driver's binary is not present.

Install the test framework [Tox](https://tox.wiki/en/latest/).

```bash
$ python3 -m pip install tox
```

### Running the test suite

Run all tests, including linting and coverage reports. This should be
run prior to merging or submitting a pull request.

```bash
$ tox
```

### List available scenarios

List all available scenarios. This is useful to target specific Python
and Ansible version for the functional and unit tests.

```bash
$ tox -av
```

### Unit

Run all unit tests with coverage.

```bash
$ tox -e py
```

Run all unit tests for a specific version of Python.

```bash
$ tox -e py311
```

### Linting

Linting is performed by a combination of linters.

Run all the linters (some perform changes to conform the code to the
style rules).

```bash
$ tox -e lint
```

### Documentation

Generate the documentation, using [mkdocs](https://www.mkdocs.org/).

```bash
$ tox -e docs
```

### Updating Dependencies

Dependencies need to be updated by hand in:

- `.config/requirements.in`
- `.pre-commit-config.yaml` (2 places)

Afterwards, you will need to generate changes to `requirements.lock.txt`
and `requirement.txt`, by running the commands listed at the top of those files.

Please note that CI will attempt to regenerate those changes, and if there is any diff, CI will fail.

## Credits

Based on the good work of John Dewey
([\@retr0h](https://github.com/retr0h)) and other
[contributors](https://github.com/ansible-community/molecule/graphs/contributors).
Active member list can be seen at [Molecule working
group](https://github.com/ansible/community/wiki/Molecule).
