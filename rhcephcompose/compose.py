import errno
import glob
import os
from rhcephcompose import Build, Comps, Variants
from rhcephcompose.log import log
from shutil import copy
import subprocess
import textwrap
import time


class Compose(object):
    """
    A "compose" is a particular "spin" or "release" . It is a collection
    of repositories.
    """

    def __init__(self, conf):
        """ This constructor simply stores all our settings; it takes no
        actions. See run() for that. """
        # Build lists are normally in the Errata Tool or a Brew tag. There's
        # no support for Ubuntu builds in Brew or the Errata Tool today, so I
        # just list each build in text files. The "builds" dict here contains
        # a text file for each distro.
        self.builds = conf['builds']
        # In Pungi terminology, assume gather_source "comps" (see also
        # Pungi's "comps_file".)
        self.comps = conf['comps']
        # Variants file copied directly from what we use with Distill on
        # RHEL.
        self.variants_file = conf['variants_file']
        # In Pungi terminology, assume pkgset_source "chacra" (instead
        # of "koji").
        self.chacra_url = conf['chacra_url']
        self.chacra_ssl_verify = conf.get('chacra_ssl_verify', True)
        # Lookaside cache location.
        # See freedesktop.org spec for XDG_CACHE_HOME
        try:
            xdg_cache_home = os.environ['XDG_CACHE_HOME']
        except KeyError:
            xdg_cache_home = os.path.expanduser('~/.cache')
        self.cache_path = os.path.join(xdg_cache_home, 'rhcephcompose')
        # Output target directory
        self.target = conf['target']
        # Product version, eg "1.3"
        self.product_version = conf['product_version']
        # Extra files to put at the root of the compose
        self.extra_files = conf['extra_files']
        # Whether sources composition should be skipped
        self.include_sources = conf.get('include_sources', True)

    @property
    def output_dir(self):
        """
        Use the same logic that pungi/compose.py uses in order come up with
        the name for the output directory. The name should be something
        like "Ceph-1.3-Ubuntu-20160922.t.0-x86_64" to match what
        distill/pungi creates.
        """
        if getattr(self, '_output_directory', None):
            return self._output_directory
        compose_date = time.strftime('%Y%m%d')
        compose_name = 'Ceph-{product_version}-{oslabel}-{arch}-{compose_date}.t.{compose_respin}'  # NOQA
        compose_respin = 0
        while 1:
            output_dir = os.path.join(self.target, compose_name.format(
                product_version=self.product_version,
                oslabel='Ubuntu',
                compose_date=compose_date,
                arch='x86_64',
                compose_respin=compose_respin
            ))
            if os.path.isdir(output_dir):
                log.info('Found prior compose dir: %s' % output_dir)
                compose_respin += 1
                continue
            log.info('Using new compose dir: %s' % output_dir)
            self._output_directory = output_dir
            return output_dir

    def run(self):
        """ High-level function to execute a compose. """
        if not os.path.isdir(self.cache_path):
            os.makedirs(self.cache_path)

        if not os.path.isdir(self.target):
            os.makedirs(self.target)

        # Make top-level output directory for this compose.
        os.mkdir(self.output_dir)

        # Top-level "sources" directory, parallel to our output_dir.
        if self.include_sources:
            sources_dir = self.output_dir + '-sources'
            os.mkdir(sources_dir)

        # Run the steps for each distro.
        for distro in self.builds.keys():
            # (We assume that all keys in self.builds also exist in
            # self.comps.)
            if distro not in self.comps.keys():
                msg = ('Loading builds for "{0}", and the comps '
                       'configuration is missing a "{0}" key. Please add a '
                       'comps XML file for this distro.').format(distro)
                raise SystemExit(msg)
            self.run_distro(distro)

        # Copy any extra files to the root of the compose.
        for extra_file in self.extra_files:
            # For "glob" type extra files, glob the compose's output_dir, and
            # copy the results to the root.
            if 'glob' in extra_file:
                glob_path = os.path.join(self.output_dir, extra_file['glob'])
                for f in glob.glob(glob_path):
                    copy(f, self.output_dir)
            # For "file" type extra files, copy the file from the user's cwd.
            if 'file' in extra_file:
                copy(os.path.join('extra_files', extra_file['file']),
                     self.output_dir)

        # create "latest" symlink
        self.symlink_latest()

    def symlink_latest(self):
        """ Create the "latest" symlink for this output_dir. """
        latest_tmpl = 'Ceph-{product_version}-{oslabel}-{arch}-latest'
        latest_path = os.path.join(self.target, latest_tmpl.format(
            product_version=self.product_version,
            oslabel='Ubuntu',
            arch='x86_64',
        ))
        try:
            os.unlink(latest_path)
        except OSError, e:
            if e.errno != errno.ENOENT:
                log.error('Problem deleting "latest" symlink')
                raise SystemExit(e)
        os.symlink(os.path.relpath(self.output_dir, start=self.target),
                   latest_path)

    def run_distro(self, distro):
        """ Execute a compose for a distro. """

        # Read the "builds_path" text file for this distro. Create a list of
        # each line of this file.
        builds_path = self.builds[distro]
        builds = [line.rstrip('\n') for line in open(builds_path)]

        log.info('Found %d build ids in "%s"' % (len(builds), builds_path))

        # Read pkg mappings from Distill-style comps XML.
        # (Assembles a master list of package names that we will need.)
        comps_file = self.comps[distro]
        comps = Comps()
        comps.parse_file(comps_file)

        # Copy the builds' files to the correct directories, according to
        # comps.xml + variants.xml.

        for build_id in builds:
            build = Build(build_id, ssl_verify=self.chacra_ssl_verify)
            # Find all the (whitelisted) binaries for this build.
            build.find_artifacts_from_chacra(chacra=self.chacra_url,
                                             whitelist=comps.all_packages)
            # Assign each binary to its respective comps group(s).
            for binary in build.binaries:
                comps.assign_binary_to_groups(binary)
            # Download all the source artifacts for this build and put them in
            # the "sources" directory.
            if self.include_sources:
                # Top-level "sources" directory, parallel to our output_dir.
                sources_dir = self.output_dir + '-sources'
                for source in build.sources:
                    source.download(cache_dir=self.cache_path,
                                    dest_dir=sources_dir)

        variants = Variants()
        variants.parse_file(self.variants_file)

        for variant_id, variant_groups in variants.items():
            # Top-level directory for this repository:
            variant_dir = os.path.join(self.output_dir, variant_id)
            if not os.path.isdir(variant_dir):
                os.mkdir(variant_dir)

            # Set up the reprepro configuration:
            log.info('Creating reprepro configuration for %s' % variant_id)
            conf_dir = os.path.join(variant_dir, 'conf')
            if not os.path.isdir(conf_dir):
                os.mkdir(conf_dir)
            distributions_path = os.path.join(conf_dir, 'distributions')
            dist_template = textwrap.dedent('''\
                Codename: {codename}
                Suite: stable
                Components: main
                Architectures: amd64 i386
                Origin: Red Hat, Inc.
                Description: Ceph distributed file system
                DebIndices: Packages Release . .gz .bz2
                DscIndices: Sources Release .gz .bz2
                Contents: .gz .bz2

            ''')
            with open(distributions_path, 'a') as dist_conf_file:
                dist_conf_file.write(dist_template.format(codename=distro))

            # Loop through all the comps groups in this variant. (in Ceph we
            # only have one group per variant, so far!)
            for group_id in variant_groups:
                # Loop through all the binaries in this comps group
                binaries = comps.groups[group_id].binaries
                msg = 'Comps group ID "%s" contains %d binaries %s'
                msg_binaries = list(map(lambda x: x.filename, binaries))
                log.info(msg % (group_id, len(binaries), msg_binaries))
                for binary in binaries:
                    # Add this binary to our variant's repo/directory:
                    self.add_binary_to_repo(binary=binary,
                                            repo_path=variant_dir,
                                            distro=distro)

    def add_binary_to_repo(self, binary, repo_path, distro):
        """ Add a binary (.deb) to a Debian repository. """
        binary.download(cache_dir=self.cache_path)
        msg = 'Running reprepro to add %s to %s distro in %s'
        log.info(msg % (binary.name, distro, repo_path))
        binary_path = os.path.join(self.cache_path, binary.filename)
        command = [
            'reprepro',
            '--ask-passphrase',
            '-b', repo_path,
            '-C', 'main',
            '--ignore=wrongdistribution',
            '--ignore=wrongversion',
            '--ignore=undefinedtarget',
            'includedeb', distro, binary_path
        ]
        log.info('running command: %s' % ' '.join(command))
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE
        )
        out, err = proc.communicate()
        exit_code = proc.wait()
        if err:
            for i in err:
                log.error(i)
        if exit_code != 0:
            msg = 'command failed with status code: %s'
            raise RuntimeError(msg % exit_code)
