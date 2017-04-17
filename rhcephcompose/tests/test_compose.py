import os
import time
import pytest
from copy import copy
from rhcephcompose.compose import Compose
from kobo.conf import PyConfigParser

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures')


class TestCompose(object):

    conf_file = os.path.join(FIXTURES_DIR, 'basic.conf')
    conf = PyConfigParser()
    conf.load_from_file(conf_file)

    def test_constructor(self):
        c = Compose(self.conf)
        assert isinstance(c, Compose)
        assert c.target == 'trees'

    @pytest.mark.parametrize(('compose_type', 'suffix'), [
        ('production', ''),
        ('nightly', '.n'),
        ('test', '.t'),
        ('ci', '.ci'),
    ])
    def test_output_dir(self, tmpdir, monkeypatch, compose_type, suffix):
        monkeypatch.chdir(tmpdir)
        conf = copy(self.conf)
        conf['compose_type'] = compose_type
        c = Compose(conf)
        compose_date = time.strftime('%Y%m%d')
        expected = 'trees/Ceph-2-Ubuntu-x86_64-{0}{1}.0'.format(
            compose_date, suffix)
        assert c.output_dir == expected

    def test_symlink_latest(self, tmpdir, monkeypatch):
        monkeypatch.chdir(tmpdir)
        c = Compose(self.conf)
        os.makedirs(c.output_dir)
        c.symlink_latest()
        result = os.path.realpath('trees/Ceph-2-Ubuntu-x86_64-latest')
        assert result == os.path.realpath(c.output_dir)

    def test_create_repo(self, tmpdir, monkeypatch):
        monkeypatch.chdir(tmpdir)
        c = Compose(self.conf)
        # TODO: use real list of binaries here
        c.create_repo(str(tmpdir), 'xenial', [])
        distributions_path = tmpdir.join('conf/distributions')
        assert distributions_path.exists()

        expected = '''\
Codename: xenial
Suite: stable
Components: main
Architectures: amd64 i386
Origin: Red Hat, Inc.
Description: Ceph distributed file system
DebIndices: Packages Release . .gz .bz2
DscIndices: Sources Release .gz .bz2
Contents: .gz .bz2

'''
        assert distributions_path.read() == expected
