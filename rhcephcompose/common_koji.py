try:
    import koji
    from koji_cli.lib import activate_session
    HAS_KOJI = True
except ImportError:
    HAS_KOJI = False


def get_session(profile):
    """
    Return an anonymous koji session for this profile name.

    :param str profile: profile name, like "koji" or "cbs"
    :returns: anonymous koji.ClientSession
    """
    # Note: this raises koji.ConfigurationError if we could not find this
    # profile name.
    # (ie. "check /etc/koji.conf.d/*.conf")
    conf = koji.read_config(profile)
    conf['authtype'] = 'noauth'
    hub = conf['server']
    session = koji.ClientSession(hub, {})
    activate_session(session, conf)
    return session


def get_koji_pathinfo(profile):
    """
    Return a Koji PathInfo object for our profile.

    :param str profile: profile name, like "koji" or "cbs"
    :returns: koji.PathInfo
    """
    conf = koji.read_config(profile)
    top = conf['topurl']  # or 'topdir' here for NFS access
    pathinfo = koji.PathInfo(topdir=top)
    return pathinfo
