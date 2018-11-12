import requests


def cache(builds, cache_dir, ssl_verify=True):
    """
    Download all the builds' artifacts into our cache directory.

    :param set builds: set of Build objects
    :param str cache_dir: path to a destination directory
    :param ssl_verify: verify HTTPS connection or not (default: True)
    """
    session = requests.Session()
    session.verify = ssl_verify
    for build in builds:
        for binary in build.binaries:
            binary.download(cache_dir, session=session)
        for source in build.sources:
            source.download(cache_dir, session=session)
