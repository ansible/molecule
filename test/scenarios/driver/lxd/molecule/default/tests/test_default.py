import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory.yml').get_hosts('all')


def test_hostname(SystemInfo):
    assert 'instance-1-default' == SystemInfo.hostname
