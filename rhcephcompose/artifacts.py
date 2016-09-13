from hashlib import sha512
import os
import re
import requests
from shutil import copy

from rhcephcompose.log import log


class PackageArtifact(object):
    """ Artifact from a Chacra build. Base class. """
    def __init__(self, url, checksum, ssl_verify=True):
        self.url = url
        self.checksum = checksum
        self.ssl_verify = ssl_verify
        self.verified_caches = set()

    @property
    def filename(self):
        """ Return the filename, eg ruby-rkerberos_0.1.3-2trusty_amd64.deb """
        return os.path.basename(self.url)

    def verify_checksum(self, cache_file):
        """
        Verify this cached file's checksum against self.checksum.

        Optimization: If this function has returned True for a particular
        cache_file, we'll save that result and return it again, to save time
        calculating the same cache_file checksum over and over.
        """
        if cache_file in self.verified_caches:
            return True
        chsum = sha512()
        with open(cache_file, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                chsum.update(chunk)
            digest = chsum.hexdigest()
        if digest == self.checksum:
            self.verified_caches.add(cache_file)
        return digest == self.checksum

    def download(self, cache_dir, dest_dir=None):
        """ Download self.url to cache_dir, then copy to dest_dir. """
        # Ensure that these args really are directories:
        if not os.path.isdir(cache_dir):
            os.makedirs(self.cache_dir)
        if dest_dir is not None and not os.path.isdir(dest_dir):
            os.makedirs(self.dest_dir)
        # Calculate the download destination in the cache_dir:
        cache_dest = os.path.join(cache_dir, self.filename)
        # Do we have a cached copy of this file, or not?
        if os.path.isfile(cache_dest):
            msg = '%s already in %s, skipping download'
            log.info(msg % (self.filename, cache_dir))
        else:
            log.info('Caching %s in %s' % (self.url, cache_dir))
            r = requests.get(self.url, stream=True, verify=self.ssl_verify)
            r.raise_for_status()
            with open(cache_dest, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
        # Sanity-check this cached file's checksum.
        if not self.verify_checksum(cache_dest):
            raise RuntimeError('%s: sha512sum is not %s' %
                               (cache_dest, self.checksum))
        if dest_dir is not None:
            copy(cache_dest, dest_dir)


class SourceArtifact(PackageArtifact):
    """ Source Artifact from chacra. """
    def __init__(self, *args, **kwargs):
        super(SourceArtifact, self).__init__(*args, **kwargs)


class BinaryArtifact(PackageArtifact):
    """ Binary Artifact from chacra (ie ".deb" file). """

    # Regex to parse the name and version of this binary.
    name_version_re = re.compile('^([^_]+)_([^_]+)')

    def __init__(self, *args, **kwargs):
        super(BinaryArtifact, self).__init__(*args, **kwargs)

    @property
    def name(self):
        """ Return the name of a Debian build, eg "ruby-rkerberos" or "ceph".
        Corresponds to "project_name" in Chacra. """
        return self.name_version_re.match(self.filename).group(1)
