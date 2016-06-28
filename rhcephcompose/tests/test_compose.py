import os
import time
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

    def test_output_dir(self, tmpdir, monkeypatch):
        monkeypatch.chdir(tmpdir)
        c = Compose(self.conf)
        compose_date = time.strftime('%Y%m%d')
        expected = 'trees/Ceph-2-Ubuntu-x86_64-%s.t.0' % compose_date
        assert c.output_dir == expected
