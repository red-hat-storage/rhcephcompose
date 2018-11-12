from hashlib import md5
import posixpath
from rhcephcompose import common_koji
from rhcephcompose.build import Build
from rhcephcompose.artifacts import BinaryArtifact, SourceArtifact
from rhcephcompose.log import log


# Koji archive types that represent a Debian source package:
SOURCE_TYPES = ('tar', 'dsc')


def query(profile, tag, whitelist):
    """
    Find all the artifacts we will need from a given Koji tag.

    :param profile: Koji profile name, eg "koji"
    :param tag: Koji tag, "ceph-3.2-xenial"
    :param whitelist: whitelist of deb package names to save
    :returns: list of rhcephcompose Build objects
    """
    if not common_koji.HAS_KOJI:
        raise RuntimeError('Please install the koji Python library')
    # Query koji for all builds in the tag.
    session = common_koji.get_session(profile)
    buildinfolist = session.listTagged(tag, inherit=True, latest=True,
                                       type='debian')
    pathinfo = common_koji.get_koji_pathinfo(profile)
    # Query koji for all files in all builds.
    builds = set()
    for buildinfo in buildinfolist:
        build = Build(buildinfo['name'])
        # Get the URL of the directory for this build.
        directory = pathinfo.typedir(buildinfo, 'debian')
        # Look up the list of files for this build.
        files = session.listArchives(buildinfo['id'])
        # Find all the .debs (and corresponding dbg .debs) in our whitelist.
        for filedata in [f for f in files if f['type_name'] == 'deb']:
            b = parse_artifact(filedata, directory)
            if b.name in whitelist:
                log.info('"%s" is in whitelist, saving' % b.name)
                build.binaries.append(b)
            if b.dbg_parent is not None and b.dbg_parent in whitelist:
                log.info('"%s" parent is in whitelist, saving' % b.name)
                build.binaries.append(b)
        # If this build had no binaries in the whitelist, skip it now.
        if not build.binaries:
            log.warning('skipping %s, no whitelisted binaries' % build.name)
            continue
        # Save the sources for this build as well.
        for filedata in [f for f in files if f['type_name'] in SOURCE_TYPES]:
            s = parse_artifact(filedata, directory)
            build.sources.append(s)
        builds.add(build)
    return builds


def parse_artifact(filedata, directory):
    """
    Parse Koji's data into an rhcephcompose.artifacts class.

    :param dict filedata: a single element from Koji's listArchives call
    :param dict directory: url to the parent directory of the files
    :returns: BinaryArtifact or SourceArtifact, or None if we could not parse
              this artifact.
    """
    opts = {'checksum': filedata['checksum'], 'checksum_method': md5}
    url = posixpath.join(directory, filedata['filename'])
    if filedata['type_name'] == 'deb':
        return BinaryArtifact(url=url, **opts)
    if filedata['type_name'] in ('tar', 'dsc'):
        return SourceArtifact(url=url, **opts)
