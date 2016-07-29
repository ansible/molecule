testinfra_hosts = ['demo1']


def test_etc_molecule_demo1(File):
    f = File('/etc/molecule/demo1')

    assert f.is_file
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o644
    assert f.contains('molecule demo1 file')


def test_etc_molecule_demo2(File):
    f = File('/etc/molecule/demo2')

    assert not f.exists
