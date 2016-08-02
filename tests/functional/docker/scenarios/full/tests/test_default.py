from testinfra.utils.ansible_runner import AnsibleRunner

testinfra_hosts = AnsibleRunner('.molecule/ansible_inventory').get_hosts('all')


def test_hosts_file(File):
    hosts = File('/etc/hosts')

    assert hosts.user == 'root'
    assert hosts.group == 'root'
