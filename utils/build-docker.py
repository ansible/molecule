#!/usr/bin/env python
"""Docker image builder for distributing molecule as a container."""

from setuptools_scm import get_version
from packaging.version import Version
import os
import sys


def run(cmd):
    """Build docker container distribution."""
    print(cmd)
    r = os.system(cmd)
    if r:
        print("ERROR: command returned {0}".format(r))
        sys.exit(r)


if __name__ == "__main__":

    version = get_version()
    version_tag = version.replace("+", "-")
    image_name = os.environ.get('QUAY_REPO', 'quay.io/ansible/molecule')

    expire = ""
    tagging_args = ""
    tags_to_push = [version_tag]
    if Version(version).is_prerelease:
        expire = "--label quay.expires-after=2w"
        mobile_tag = "master"
        tags_to_push.append(mobile_tag)
    else:
        # we have a release
        mobile_tag = "latest"
        tagging_args += "-t " + image_name + ":latest "
        tags_to_push.append("latest")
    # if on master, we want to also move the master tag
    if os.environ.get('TRAVIS_BRANCH', None) == 'master':
        tagging_args += "-t " + image_name + ":master "
        tags_to_push.append("master")

    print("Building version {0}".format(version_tag))
    run(
        "docker build --network host --pull "
        "-t {0}:{1} {2} {3} .".format(image_name, version_tag, tagging_args, expire)
    )

    # Decide to push when all conditions below are met:
    if os.environ.get('TRAVIS_BUILD_STAGE_NAME', None) == 'deploy':
        run("docker login quay.io")
        for tag in tags_to_push:
            run("docker push {0}:{1}".format(image_name, tag))
