import os
from rhcephcompose.variants import Variants

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures')


class TestVariants(object):

    def test_constructor(self):
        v = Variants()
        assert v == {}

    def test_parse_basic_file(self):
        v = Variants()
        fixture_file = os.path.join(FIXTURES_DIR, 'variants-basic.xml')
        v.parse_file(fixture_file)
        assert 'Tools' in v
        # Test that the "Tools" variant contains the "ceph-tools" comps group.
        assert v['Tools'] == ['ceph-tools']
