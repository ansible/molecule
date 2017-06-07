import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('group1')


def test_resolve(host):
    group1 = ['instance1', 'instance2']
    group2 = ['instance3', 'instance4']

    for instance in group1:
        cmd = host.run('getent ahostsv4 {}'.format(instance))
        assert cmd.rc == 0
    for instance in group2:
        cmd = host.run('getent ahostsv4 {}'.format(instance))
        assert cmd.rc != 0
