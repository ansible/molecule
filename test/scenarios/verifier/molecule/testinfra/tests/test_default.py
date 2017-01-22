import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory.yml').get_hosts('all')


def test_ansible_hostname(File):
    f = File('/tmp/molecule/instance-1')

    assert not f.exists
