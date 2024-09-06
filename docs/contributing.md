# Contributing

Noticed a bug or have an idea to improve Ansible Molecule?
Want to write some documentation or share your expertise on the forum?
There are many ways to get involved and contribute, find out how.

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

## Talk to us

Connect with the Ansible community!

Join the Ansible forum to ask questions, get help, and interact with the
community.

- [Get Help](https://forum.ansible.com/c/help/6): get help or help others.
  Please add appropriate tags if you start new discussions, for example use the
  `molecule`, `molecule6`, or `devtools` tags.
- [Social Spaces](https://forum.ansible.com/c/chat/4): meet and interact with
  fellow enthusiasts.
- [News & Announcements](https://forum.ansible.com/c/news/5): track project-wide
  announcements including social events.

To get release announcements and important changes from the community, see the
[Bullhorn newsletter](https://docs.ansible.com/ansible/devel/community/communication.html#the-bullhorn).

You can find more information in the
[Ansible communication guide](https://docs.ansible.com/ansible/devel/community/communication.html).

Possible security bugs should be reported via email to
<mailto:security@ansible.com>.

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

## Credits

Based on the good work of John Dewey
([\@retr0h](https://github.com/retr0h)) and other
[contributors](https://github.com/ansible-community/molecule/graphs/contributors).
Active member list can be seen at [Molecule working
group](https://github.com/ansible/community/wiki/Molecule).
