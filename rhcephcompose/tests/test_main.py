import os
import sys
import rhcephcompose
from rhcephcompose import main
import pytest


@pytest.fixture
def conf(fixtures_dir):
    return os.path.join(fixtures_dir, 'basic.conf')


class FakeCompose(object):
    def run(self):
        pass


class ComposeRecorder(object):
    """ Record the arg to the Compose object's constructor. """
    def __call__(self, conf):
        self.conf = conf
        return FakeCompose()


class TestMain(object):

    def test_constructor(self, conf, monkeypatch):
        monkeypatch.setattr(sys, 'argv', ['rhcephcompose', conf])
        recorder = ComposeRecorder()
        monkeypatch.setattr(main, 'Compose', recorder)
        main.RHCephCompose()
        expected = {
            'builds': {'trusty': 'builds-ceph-2.0-trusty.txt',
                       'xenial': 'builds-ceph-2.0-xenial.txt'},
            'chacra_url': 'https://chacra.example.com/',
            'compose_type': 'test',
            'comps': {'trusty': 'comps-basic.xml'},
            'extra_files': [{'file': 'README'}, {'file': 'EULA'},
                            {'file': 'GPL'}],
            'release_short': 'RHCEPH',
            'release_version': '2.0',
            'target': 'trees',
            'variants_file': 'variants-basic.xml'
        }
        assert recorder.conf == expected

    def test_insecure(self, conf, monkeypatch):
        monkeypatch.setattr(sys, 'argv', ['rhcephcompose', '--insecure', conf])
        recorder = ComposeRecorder()
        monkeypatch.setattr(main, 'Compose', recorder)
        main.RHCephCompose()
        assert recorder.conf['chacra_ssl_verify'] is False

    def test_version(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, 'argv', ['rhcephcompose', '--version'])
        with pytest.raises(SystemExit):
            main.RHCephCompose()
        out, err = capsys.readouterr()
        expected = "rhcephcompose %s\n" % rhcephcompose.__version__
        # py34 and newer print to stdout.
        if sys.version_info >= (3, 4):
            assert out == expected
        else:
            assert err == expected
