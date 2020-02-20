#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Testinfra tests."""


def test_ansible_hostname(host):
    """Validate hostname."""
    f = host.file("/tmp/molecule/instance-1")
    assert not f.exists
