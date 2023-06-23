# Continuous integration

Molecule output will use `ANSI` colors if stdout is an interactive TTY
and `TERM` value seems to support it. You can define `PY_COLORS=1` to
force use of `ANSI` colors, which can be handy for some CI systems.

## GitHub Actions

[GitHub Actions](https://github.com/features/actions) runs a CI
pipeline, much like any others, that's built into GitHub.

An action to clone a repo as `molecule_demo`, and run `molecule test` in
ubuntu.

```yaml
---
name: Molecule Test
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      max-parallel: 4
      matrix:
        python-version: ["3.9", "3.10"]

    steps:
      - uses: actions/checkout@v2
        with:
          path: molecule_demo
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python3 -m pip install --upgrade pip
          python3 -m pip install -r requirements.txt
      - name: Test with molecule
        run: |
          molecule test
```

If you need access to requirements in private repositories, [create a
token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)
with the required privileges, then define a `GIT_CREDENTIALS` secret for
your repository with a value looking like
`https://username:token@github.com/`, and finally add the
following step before "Test with molecule".

```yaml
- name: Setup git credentials
  uses: fusion-engineering/setup-git-credentials@v2
  with:
    credentials: ${{secrets.GIT_CREDENTIALS}}
```

## Travis CI

[Travis](https://travis-ci.com/) is a CI platform, which can be used to
test Ansible roles.

A `.travis.yml` testing a role named foo1 with the Docker driver.

```yaml
---
sudo: required
language: python
services:
  - docker
install:
  - python3 -m pip install molecule
  # - python3 -m pip install required driver (e.g. docker, shade, boto, apache-libcloud)
script:
  - molecule test
```

A `.travis.yml` using [Tox](https://tox.readthedocs.io/en/latest) as
described below.

```yaml
---
sudo: required
language: python
services:
  - docker
install:
  - python3 -m pip install tox-travis
script:
  - tox
```

## Gitlab CI

[Gitlab](https://gitlab.com) includes its own CI. Pipelines are usually
defined in `.gitlab-ci.yml` file in the top folder of a repository, to
be run on Gitlab Runners.

Here is an example using Docker in Docker

```yaml
---
image: docker:stable-dind

services:
  - docker:dind

before_script:
  - apk add --no-cache
    python3 python3-dev py3-pip gcc git curl build-base
    autoconf automake py3-cryptography linux-headers
    musl-dev libffi-dev openssl-dev openssh
  - docker info
  - python3 --version
  - python3 -m pip install ansible molecule-plugins[docker]
  - ansible --version
  - molecule --version

molecule:
  stage: test
  script:
    - cd roles/testrole && molecule test
```

GitLab Runner is used to run your jobs and send the results back to
GitLab. By tagging a Runner for the types of jobs it can handle, you can
make sure shared Runners will only run the jobs they are equipped to
run.

Here is another example using Docker, virtualenv and tags on Centos 7.

```yaml
---
stages:
  - test

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip"
  GIT_STRATEGY: clone

cache:
  paths:
    - .pip/
    - virtenv/

before_script:
  - python -V
  - pip install virtualenv
  - virtualenv virtenv
  - source virtenv/bin/activate
  - pip install ansible molecule docker
  - ansible --version
  - molecule --version
  - docker --version

molecule:
  stage: test
  tags:
    - molecule-jobs
  script:
    - molecule test
```

## Azure Pipelines

[Azure
Pipelines](https://azure.microsoft.com/en-gb/services/devops/pipelines/)
projects rely on the `azure-pipelines.yml` file within the root folder
of a repository. There are a number of pre-requisites for running CI/CD
within Azure on self-hosted runners if you intend on using the
`UsePythonVersion` task. Details of this can be found in the [Use Python
Version
Task](https://docs.microsoft.com/en-us/azure/devops/pipelines/tasks/tool/use-python-version?view=azure-devops)
documentation.

```yaml
---
trigger:
  - main

pool:
  vmImage: ubuntu-16.04

steps:
  - checkout: git://project-name/role-name
    path: role-name

  - task: UsePythonVersion@0
    inputs:
      versionSpec: "3.9"

  - script: python -m pip install "molecule[lint]" "python-vagrant" "molecule-vagrant" "ansible"
    displayName: Install dependencies

  - script: python -m pip install "python-tss-sdk"
    displayName: Role-specific dependencies

  - script: |
      export PATH="$PATH:/home/<user>/.local/bin/"
      cd $(Agent.BuildDirectory)/role-name
      molecule test
    displayName: Test relevant platforms
```

Whilst the pipeline checks out your code initially as part of the
pipeline task, by default, it checks it out into a directory named `s`
within `$(Agent.BuildDirectory)`. If you checkout one other repository,
the `s` is substituted with the path provided in that checkout. If you
checkout multiple roles (e.g. some private roles within your Azure
organisation) then the `s` structure is used, hence the importance of
the `cd $(Agent.BuildDirectory)/role-name` which ensures you are in the
correct directory regardless of format. Check the [Azure Build
Variables](https://docs.microsoft.com/en-us/azure/devops/pipelines/build/variables?view=azure-devops&tabs=yaml#build-variables-devops-services)
documentation for more detailed information on these.

The `export PATH` is required to ensure you can use the
`molecule`/`ansible` shell scripts. Azure doesn't add these by default.

## Jenkins Pipeline

[Jenkins](https://jenkins.io/doc/book/pipeline/jenkinsfile) projects can
also be defined in a file, by default named `Jenkinsfile` in the top
folder of a repository. Two syntax are available, Declarative and
Scripted. Here is an example using the declarative syntax, setting up a
virtualenv and testing an Ansible role via Molecule.

```groovy
pipeline {

  agent {
    // Node setup : minimal centos7, plugged into Jenkins, and
    // git config --global http.sslVerify false
    // sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
    // sudo yum -y install python36u python36u-pip python36u-devel git curl gcc
    // git config --global http.sslVerify false
    // sudo curl -fsSL get.docker.com | bash
    label 'Molecule_Slave'
  }

  stages {

    stage ('Get latest code') {
      steps {
        checkout scm
      }
    }

    stage ('Setup Python virtual environment') {
      steps {
        sh '''
          export HTTP_PROXY=http://10.123.123.123:8080
          export HTTPS_PROXY=http://10.123.123.123:8080
          python3 -m pip install virtualenv
          virtualenv virtenv
          source virtenv/bin/activate
          python3 -m pip install --upgrade ansible molecule docker
        '''
      }
    }

    stage ('Display versions') {
      steps {
        sh '''
          source virtenv/bin/activate
          docker -v
          python -V
          ansible --version
          molecule --version
        '''
      }
    }

    stage ('Molecule test') {
      steps {
        sh '''
          source virtenv/bin/activate
          molecule test
        '''
      }
    }

  }

}
```

The following Jenkinsfile uses the [Ansible Creator
Execution Environment](https://github.com/ansible/creator-ee) image.

```groovy
pipeline {
  agent {
    docker {
      image 'quay.io/ansible/creator-ee'
      args '-v /var/run/docker.sock:/var/run/docker.sock'
    }
  }

  stages {

    stage ('Display versions') {
      steps {
        sh '''
          docker -v
          python -V
          ansible --version
          molecule --version
        '''
      }
    }

    stage ('Molecule test') {
      steps {
        sh 'sudo molecule test --all'
      }
    }

  } // close stages
}   // close pipeline
```

!!! note

    For Jenkins to work properly using a Multibranch Pipeline
    or a GitHub Organisation - as used by Blue Ocean, the role
    name in the scenario converge.yml should be changed to perform a lookup
    of the role root directory. For example :

    ``` yaml
    ---
    - name: Converge
      hosts: all
      roles:
        - role: "{{ lookup('env', 'MOLECULE_PROJECT_DIRECTORY') | basename }}"
    ```

    This is the cleaner of the current choices. See
    [issue1567_comment](https://github.com/ansible-community/molecule/issues/1567#issuecomment-436876722)
    for additional detail.

## Tox

[Tox](https://tox.wiki/en/latest/) is a generic virtualenv
management, and test command line tool.
[Tox](https://tox.wiki/en/latest/) can be used in conjunction
with
[Factors](https://tox.wiki/en/latest/config.html#factors-and-factor-conditional-settings)
and Molecule, to perform scenario tests.

To test the role against multiple versions of Ansible.

```ini
[tox]
minversion = 1.8
envlist = py{27}-ansible{20,21,22}
skipsdist = true

[testenv]
passenv = *
deps =
    -rrequirements.txt
    ansible20: ansible==2.0.2.0
    ansible21: ansible==2.1.2.0
    ansible22: ansible==2.2.0.0
commands =
    molecule test
```

To view the factor generated tox environments run `tox -l`.

If using the [\--parallel
functionality](https://tox.wiki/en/latest/config.html#cmdoption-tox-p)
of Tox (version 3.7 onwards), Molecule must be made aware of the
parallel testing by setting a `MOLECULE_EPHEMERAL_DIRECTORY` environment
variable per environment. In addition, we export a `TOX_ENVNAME`
environment variable, it's the name of our tox env.

```ini
[tox]
minversion = 3.7
envlist = py{36}_ansible{23,24}
skipsdist = true

[testenv]
deps =
    -rrequirements.txt
    ansible23: ansible==2.3
    ansible24: ansible==2.4
commands =
    molecule test
setenv =
    TOX_ENVNAME={envname}
    MOLECULE_EPHEMERAL_DIRECTORY=/tmp/{envname}
```

You also must include the `TOX_ENVNAME` variable in name of each
platform in `molecule.yml` configuration file. This way, their names
won't create any conflict.

```yaml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance1-$TOX_ENVNAME
    image: mariadb
  - name: instance2-$TOX_ENVNAME
    image: retr0h/centos7-systemd-ansible:latest
    privileged: True
    command: /usr/sbin/init
provisioner:
  name: ansible
verifier:
  name: testinfra
```
