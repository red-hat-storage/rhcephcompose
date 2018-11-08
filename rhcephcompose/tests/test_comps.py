import os
from rhcephcompose.comps import Comps


class TestComps(object):

    def test_constructor(self):
        c = Comps()
        assert c.all_packages == set()
        assert c.groups == {}

    def test_parse_basic_file(self, fixtures_dir):
        c = Comps()
        fixture_file = os.path.join(fixtures_dir, 'comps-basic.xml')
        c.parse_file(fixture_file)
        assert 'calamari-server' in c.all_packages
        assert 'calamari' in c.groups
