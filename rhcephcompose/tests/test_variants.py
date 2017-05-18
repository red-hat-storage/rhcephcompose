import os
from rhcephcompose.variants import Variants


class TestVariants(object):

    def test_constructor(self):
        v = Variants()
        assert v == {}

    def test_parse_basic_file(self, fixtures_dir):
        v = Variants()
        fixture_file = os.path.join(fixtures_dir, 'variants-basic.xml')
        v.parse_file(fixture_file)
        assert 'Tools' in v
        # Test that the "Tools" variant contains the "ceph-tools" comps group.
        assert v['Tools'] == ['ceph-tools']
