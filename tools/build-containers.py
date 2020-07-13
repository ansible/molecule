#!/usr/bin/env python
"""Docker image builder for distributing molecule as a container."""

import os
import socket
import sys
from shutil import which

from packaging.version import Version
from setuptools_scm import get_version


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
    image_name = os.environ.get("QUAY_REPO", "quay.io/ansible/molecule")

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
    if os.environ.get("TRAVIS_BRANCH", None) == "master":
        tagging_args += "-t " + image_name + ":master "
        tags_to_push.append("master")

    engine = which("podman") or which("docker")
    engine_opts = ""
    # hack to avoid apk fetch getting stuck on systems where host machine has ipv6 enabled
    # as containers support for IPv6 is almost for sure not working on both docker/podman.
    # https://github.com/gliderlabs/docker-alpine/issues/307
    # https://stackoverflow.com/a/41497555/99834
    if not engine:
        raise NotImplementedError("Unsupported container engine")
    elif engine.endswith("podman"):
        # https://github.com/containers/libpod/issues/5403
        ip = socket.getaddrinfo("dl-cdn.alpinelinux.org", 80, socket.AF_INET)[0][4][0]
        engine_opts = "--add-host dl-cdn.alpinelinux.org:" + ip

    print(f"Building version {version_tag} using {engine} container engine")
    # using '--network host' may fail in some cases where not specifying the
    # network works fine.
    run(
        f"{engine} build {engine_opts} --pull "
        f"-t {image_name}:{version_tag} {tagging_args} {expire} ."
    )

    # Decide to push when all conditions below are met:
    if os.environ.get("TRAVIS_BUILD_STAGE_NAME", None) == "deploy":
        run(f"{engine} login quay.io")
        for tag in tags_to_push:
            run(f"{engine} push {image_name}:{tag}")
