``rhcephcompose``
=================

**Note: this tool is unmaintained. Red Hat does not publish Red Hat Ceph
Storage for Ubuntu any more, so we do not maintain this tool any more.**

A tool to gather build artifacts and assemble them into a set of repositories.

``rhcephcompose`` is a distribution compose tool, similar to Red Hat's `Pungi
<https://pagure.io/pungi/>`_ (open-source). In contrast to simply throwing all
builds together into a single package repository, these tools give the user
fine-grained control over the selection of builds and the layout of the final
product's output.

Composes are release snapshots that contain release deliverables such as
installation trees with RPMs and Yum repodata. ``rhcephcompose`` creates an
installation tree for Ubuntu packages. In Red Hat we use it for developing and
shipping the RH Ceph Storage product for Ubuntu.


See Also
--------
* ``rhcephcompose`` interacts with `Koji instance <https://pagure.io/koji>`_
  or a `Chacra <https://github.com/ceph/chacra>`_ instance. It queries Koji's
  API or Chacra's API for build information and downloads build artifacts
  stored there. (This is a bit similar to the way Pungi interacts with Koji.)

* After creating a compose, you may wish to GPG-sign it with `Merfi
  <https://pypi.python.org/pypi/merfi>`_.


Note regarding Distro version
-----------------------------

In the RHEL world, el6 and el7 repositories are typically separated into two
entirely different trees in the filesystem. In Debian, a repository can mix
several distribution versions together.

Using Koji, we can tag one build with multiple -candidate tags. In other
words, we can tag "ceph-ansible-3.2.0-2redhat1" as both
"ceph-3.2-xenial-candidate" and "ceph-3.2-bionic-candidate".

In dist-git for Ubuntu, I store the branches as "-ubuntu" in order to combine
the codebase for "-trusty" and "-xenial". The reason for this is that I always
ended up keeping "ceph-1.2-rhel-6" and "ceph-1.2-rhel-7" identical, and it was
a pain to do that manually.

Caching
-------

To save time when accessing chacra, rhcephcompose downloads all build
artifacts to a local cache by default. This cache location is
``$XDG_CACHE_HOME/rhcephcompose/``. If the ``XDG_CACHE_HOME`` environment
variable is unset, rhcephcompose defaults this to ``~/.cache`` (so builds are
written to ``~/.cache/rhcephcompose``).

rhcephcompose never evicts items from this cache so it can grow without bound.
It's a good idea to clean it out occasionally. If you are running
rhcephcompose with Jenkins, you can do this automatically by setting
``$XDG_CACHE_HOME`` to a location within the job's workspace, and then have
Jenkins simply clean up the workspace.

Metadata
--------

rhcephcompose writes some metadata about the compose into a ``metadata``
subdirectory. You can read the basic ``composeinfo.json`` file with productmd
`productmd <https://github.com/release-engineering/productmd>`_ . rhcephcompose
also writes a custom ``debs.json`` file with a list of all the builds in each
distribution.

SSL errors
----------

This is more of a python-requests thing, but if you receive an SSL warning,
it's probably because you don't have the Red Hat IT CA set up for your Python
environment. Particularly if you're running this in a virtualenv, you'll want
to set the following configuration variable::

    REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/source/anchors/RH-IT-Root-CA.crt

Where "RH-IT-Root-CA.crt" is the public cert that signed the Chacra server's
HTTPS certificate.
