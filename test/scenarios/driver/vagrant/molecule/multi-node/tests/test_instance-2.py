import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('instance-2')


def test_distro(host):
    f = host.file('/etc/redhat-release')

    assert f.is_file


def test_cpus(host):
    cpus = host.ansible("setup")['ansible_facts']['ansible_processor_vcpus']

    assert 2 == int(cpus)


def test_memory(host):
    total_memory = host.ansible(
        "setup")['ansible_facts']['ansible_memtotal_mb']

    assert (1024 + 1024 / 2) <= int(total_memory) <= 2048


def test_does_not_have_shared_directory(host):
    f = host.file('/vagrant')

    assert not f.is_directory


def test_internal_interface(host):
    assert '192.168.0.2' in host.interface('eth2').addresses
