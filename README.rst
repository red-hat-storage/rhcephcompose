``rhcephcompose``
=================

.. image:: https://travis-ci.org/red-hat-storage/rhcephcompose.svg?branch=master
             :target: https://travis-ci.org/red-hat-storage/rhcephcompose

.. image:: https://badge.fury.io/py/rhcephcompose.svg
                :target: https://badge.fury.io/py/rhcephcompose

A tool to gather build artifacts and assemble them into a set of repositories.

``rhcephcompose`` is a distribution compose tool, similar to Red Hat's `Pungi
<https://pagure.io/pungi/>`_ (open-source) or Distill (closed-source). In
contrast to simply throwing all builds together into a single package
repository, these tools give the user fine-grained control over the selection
of builds and the layout of the final product's output.

Composes are release snapshots that contain release deliverables such as
installation trees with RPMs and Yum repodata. ``rhcephcompose`` creates an
installation tree for Ubuntu packages. In Red Hat we use it for developing and
shipping the RH Ceph Enterprise product for Ubuntu.


See Also
--------
* ``rhcephcompose`` interacts with a `Chacra
  <https://pypi.python.org/pypi/merfi>`_ instance. It queries Chacra's
  API for build information and downloads build artifacts stored in Chacra.
  (This is a bit similar to the way Pungi and Distill interact with Koji.)

* After creating a compose, you may wish to GPG-sign it with `Merfi
  <https://pypi.python.org/pypi/merfi>`_.


Note regarding Distro version
-----------------------------

In the RHEL world, el6 and el7 repositories are typically separated into two
entirely different trees in the filesystem. In Debian, a repository can mix
several distribution versions together.

Chacra has an API for ``distro_version``. Since we combine both Trusty and
Xenial for some packages, this introduces complexity. So I store all binaries
in "distro_version" of "all", and then use the XML and builds to determine what
should be tagged with what.

In a Brew world, we would be able to tag one build with multiple -candidate
tags, but in Chacra there is only a one-to-one relationship between builds and
distro_versions. So with Brew, we'd be able to tag "ceph-deploy-1.2.3" as both
"ceph-1.3-trusty-candidate" and "ceph-1.3-xenial-candidate", but in Chacra I
can't easily do that for individual builds.

In dist-git for Ubuntu, I store the branches as "-ubuntu" in order to combine
the codebase for "-trusty" and "-xenial". The reason for this is that I always
ended up keeping "ceph-1.2-rhel-6" and "ceph-1.2-rhel-7" identical, and it was
a pain to do that manually. As described above, I also keep all the builds
"combined" within Chacra.

SSL errors
----------

This is more of a python-requests thing, but if you receive an SSL warning,
it's probably because you don't have the Red Hat IT CA set up for your Python
environment. Particularly if you're running this in a virtualenv, you'll want
to set the following configuration variable::

    REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/source/anchors/RH-IT-Root-CA.crt

Where "RH-IT-Root-CA.crt" is the public cert that signed the Chacra server's
HTTPS certificate.
