import os
import sys
from rhcephcompose import main
from rhcephcompose.compose import Compose

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures')


class TestMain(object):

    def test_constructor(self, monkeypatch):
        conf = os.path.join(FIXTURES_DIR, 'basic.conf')
        monkeypatch.setattr(sys, 'argv', ['rhcephcompose', conf])
        monkeypatch.setattr(Compose, 'run', lambda x: None)
        main.RHCephCompose()
