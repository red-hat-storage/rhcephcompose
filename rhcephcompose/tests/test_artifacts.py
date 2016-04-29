from rhcephcompose.artifacts import BinaryArtifact, SourceArtifact


class TestArtifacts(object):

    def test_binary(self):
        url = 'http://chacra.example.com/mypackage_1.0-1.deb'
        b = BinaryArtifact(url=url)
        assert b.filename == 'mypackage_1.0-1.deb'
        assert b.name == 'mypackage'

    def test_source(self):
        url = 'http://chacra.example.com/mypackage_1.0-1.dsc'
        b = SourceArtifact(url=url)
        assert b.filename == 'mypackage_1.0-1.dsc'
