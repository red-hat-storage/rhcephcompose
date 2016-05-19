import posixpath
import re

import requests

from rhcephcompose.artifacts import BinaryArtifact, SourceArtifact
from rhcephcompose.log import log


class Build(object):
    # Regex to parse the name and version of this build.
    name_version_re = re.compile('^([^_]+)_([^_]+)')

    def __init__(self, build_id, ssl_verify=True):
        self.build_id = build_id
        self.ssl_verify = ssl_verify
        # A "Build" contains several "Binaries" and "Sources".
        self.binaries = []
        self.sources = []

    @property
    def name(self):
        """ Return the name of a Debian build, eg "ruby-rkerberos" or "ceph".
        Corresponds to "project_name" in Chacra. """
        return self.name_version_re.search(self.build_id).group(1)

    @property
    def version(self):
        """ Return version number (version+release) of a Debian build.
            Corresponds to "version" in Chacra. """
        return self.name_version_re.search(self.build_id).group(2)

    def get_chacra_build_url(self, chacra_url):
        """ Return a URL to this build's artifacts in chacra. """
        pieces = [chacra_url, 'binaries', self.name, self.version, 'ubuntu',
                  'all']
        return posixpath.join(*pieces)

    def find_artifacts_from_chacra(self, chacra, whitelist):
        """ Populate self.binaries and self.sources """
        log.info('Searching chacra %s for whitelisted binaries' % chacra)
        build_url = self.get_chacra_build_url(chacra)
        r = requests.get(build_url, verify=self.ssl_verify)
        r.raise_for_status()
        build_data = r.json()
        # Find binary deb for arches we care about.
        for arch in ['noarch', 'amd64']:
            if arch not in build_data:
                continue
            log.info('Arch "%s" has %d pkgs' % (arch, len(build_data[arch])))
            for binary in build_data[arch]:
                log.info('Found "%s" binary package artifact' % binary)
                binary_url = posixpath.join(build_url, arch, binary)
                b = BinaryArtifact(url=binary_url, ssl_verify=self.ssl_verify)
                if b.name in whitelist:
                    log.info('"%s" is in whitelist, saving' % b.name)
                    # This package is listed in comps.xml, so we care
                    # about this one. Save it in the lookaside cache.
                    self.binaries.append(b)
                else:
                    # This package is not listed in comps.xml. Skip it.
                    log.info('"%s" pkg not whitelisted, skipping' % b.name)
        # Find sources for this build.
        if 'source' not in build_data:
            msg = 'Build "%s" has no source artifacts in chacra'
            log.error(msg % self.build_id)
            exit(1)
        for source in build_data['source']:
            log.info('Found "%s" source package artifact' % source)
            source_url = posixpath.join(build_url, 'source', source)
            s = SourceArtifact(url=source_url, ssl_verify=self.ssl_verify)
            self.sources.append(s)
