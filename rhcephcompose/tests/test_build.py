from rhcephcompose.build import Build


class TestBuild(object):

    def test_constructor(self):
        b = Build('mypackage_1.0-1')
        assert b.build_id == 'mypackage_1.0-1'
        assert b.name == 'mypackage'
        assert b.version == '1.0-1'
        assert b.binaries == []
        assert b.sources == []
