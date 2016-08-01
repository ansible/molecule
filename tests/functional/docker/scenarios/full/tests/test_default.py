def test_hosts_file(File):
    hosts = File('/etc/hosts')

    assert hosts.user == 'root'
    assert hosts.group == 'root'
