#!/usr/bin/python
# -*- coding: utf-8 -*-


def test_ansible_hostname(host):
    f = host.file('/tmp/molecule/instance-1')
    assert not f.exists
