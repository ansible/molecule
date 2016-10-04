from testinfra.utils.ansible_runner import AnsibleRunner

testinfra_hosts = AnsibleRunner('.molecule/ansible_inventory').get_hosts('all')


def test_hosts_file(File):
    f = File('/tmp/check')

    assert not f.exists
