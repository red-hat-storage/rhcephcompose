from rhcephcompose.artifacts import BinaryArtifact, SourceArtifact


class TestArtifacts(object):

    deb_url = 'http://chacra.example.com/mypackage_1.0-1.deb'
    dsc_url = 'http://chacra.example.com/mypackage_1.0-1.dsc'

    def test_binary(self):
        b = BinaryArtifact(url=self.deb_url, checksum=None)
        assert b.filename == 'mypackage_1.0-1.deb'
        assert b.name == 'mypackage'

    def test_source(self):
        b = SourceArtifact(url=self.dsc_url, checksum=None)
        assert b.filename == 'mypackage_1.0-1.dsc'
