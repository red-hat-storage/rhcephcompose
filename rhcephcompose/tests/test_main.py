import os
import sys
from rhcephcompose import main
from rhcephcompose.compose import Compose


class TestMain(object):

    def test_constructor(self, fixtures_dir, monkeypatch):
        conf = os.path.join(fixtures_dir, 'basic.conf')
        monkeypatch.setattr(sys, 'argv', ['rhcephcompose', conf])
        monkeypatch.setattr(Compose, 'run', lambda x: None)
        main.RHCephCompose()
