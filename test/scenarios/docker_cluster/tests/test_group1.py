import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('group1')


def test_resolve(Command):
    group1 = ['test1.mycluster', 'test2.mycluster']
    group2 = ['test3.mycluster', 'test4.mycluster']

    for host in group1:
        cmd = Command('getent ahostsv4 {}'.format(host))
        assert cmd.rc == 0
    for host in group2:
        cmd = Command('getent ahostsv4 {}'.format(host))
        assert cmd.rc != 0
