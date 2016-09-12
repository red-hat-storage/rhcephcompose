from rhcephcompose.artifacts import BinaryArtifact, SourceArtifact


class TestArtifacts(object):

    deb_url = 'http://chacra.example.com/mypackage_1.0-1.deb'
    dsc_url = 'http://chacra.example.com/mypackage_1.0-1.dsc'

    def test_binary(self):
        b = BinaryArtifact(url=self.deb_url, checksum=None)
        assert b.filename == 'mypackage_1.0-1.deb'
        assert b.name == 'mypackage'
        assert b.dbg_parent is None

    def test_source(self):
        b = SourceArtifact(url=self.dsc_url, checksum=None)
        assert b.filename == 'mypackage_1.0-1.dsc'

    def test_verify_checksum(self, tmpdir):
        cache_file = tmpdir.join('mypackage_1.0-1.deb')
        try:
            cache_file.write_binary(b'testpackagecontents')
        except AttributeError:
            # python-py < v1.4.24 does not support write_binary()
            cache_file.write('testpackagecontents')
        checksum = 'cce64bfb35285d9c5d82e0a083cafcc6afa3292b84b26f567d92ea8ccd420e57881c9218e718c73a2ce23af53ad05ab54f168cd28ee1b5ca7ca23697fa887e1e'  # NOQA
        b = BinaryArtifact(url=self.deb_url, checksum=checksum)
        assert b.verify_checksum(str(cache_file)) is True

    def test_verify_checksum_failure(self, tmpdir):
        cache_file = tmpdir.join('mypackage_1.0-1.deb')
        try:
            cache_file.write_binary(b'testpackagecontents')
        except AttributeError:
            # python-py < v1.4.24 does not support write_binary()
            cache_file.write('testpackagecontents')
        checksum = 'INCORRECTSHA256HASH'
        b = BinaryArtifact(url=self.deb_url, checksum=checksum)
        assert b.verify_checksum(str(cache_file)) is False

    def test_dbg(self):
        url = 'http://chacra.example.com/mypackage-dbg_1.0-1.deb'
        b = BinaryArtifact(url=url)
        assert b.name == 'mypackage-dbg'
        assert b.dbg_parent == 'mypackage'
