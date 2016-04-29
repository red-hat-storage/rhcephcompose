import os
from rhcephcompose.comps import Comps

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures')


class TestComps(object):

    def test_constructor(self):
        c = Comps()
        assert c.all_packages == []
        assert c.groups == {}

    def test_parse_basic_file(self):
        c = Comps()
        fixture_file = os.path.join(FIXTURES_DIR, 'comps-basic.xml')
        c.parse_file(fixture_file)
        assert 'calamari-server' in c.all_packages
        assert 'calamari' in c.groups
