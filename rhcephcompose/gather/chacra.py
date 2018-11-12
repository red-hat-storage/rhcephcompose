from rhcephcompose import Build
from rhcephcompose.log import log


def query(builds_file, chacra_url, whitelist, ssl_verify):
    """
    Find all the artifacts we will need from a given build list text file.

    :param builds_file: "builds" text file for a distro.
    :param chacra_url: chacra server to query
    :param whitelist: whitelist of deb package names to save
    :param ssl_verify: verify HTTPS connection or not
    :returns: list of rhcephcompose Build objects
    """
    build_ids = [line.rstrip('\n') for line in open(builds_file)]

    log.info('Found %d build ids in "%s"' % (len(build_ids), builds_file))

    builds = []
    for build_id in build_ids:
        build = Build(build_id, ssl_verify=ssl_verify)
        build.find_artifacts_from_chacra(chacra=chacra_url,
                                         whitelist=whitelist)
        if not build.binaries:
            raise RuntimeError('no binaries whitelisted for %s' % build_id)
        builds.append(build)
    return builds
