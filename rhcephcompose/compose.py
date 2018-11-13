import errno
import glob
import os
from rhcephcompose import Comps, Variants
from rhcephcompose import gather
from rhcephcompose.gather import chacra
from rhcephcompose.log import log
from shutil import copy
import subprocess
import textwrap
import time

COMPOSE_TYPE_MAP = {
    'production': '',
    'nightly': '.n',
    'test': '.t',
    'ci': '.ci',
}


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
        # Variants file copied directly from what we use with Pungi on
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
        # Short name, eg "RHCEPH"
        self.release_short = conf['release_short']
        # Release version, eg "1.3"
        try:
            self.release_version = conf['release_version']
        except KeyError:
            # backwards compatibility option for old configurations
            self.release_version = conf['product_version']
        # Extra files to put at the root of the compose
        self.extra_files = conf['extra_files']
        # Whether sources composition should be included or skipped
        self.include_sources = conf.get('include_sources', True)
        # Compose type for output directory name
        self.compose_type = conf.get('compose_type', 'test')
        # Whether -dbg composition should be included or skipped
        self.include_dbg = conf.get('include_dbg', True)

    def validate(self):
        """
        Sanity-check that files exist before we go to the work of running.
        """
        # builds lists
        self.validate_builds_lists()
        # comps XML
        for comps_file in self.comps.values():
            if not os.access(comps_file, os.R_OK):
                raise RuntimeError('Unreadable comps file %s' % comps_file)
        # variants XML
        if not os.access(self.variants_file, os.R_OK):
            raise RuntimeError('Unreadable variants file %s' %
                               self.variants_file)
        # extra_files
        for extra_file in self.extra_files:
            # For "file" type extra files, we expect it in the user's cwd.
            if 'file' in extra_file:
                src = os.path.join('extra_files', extra_file['file'])
                if not os.access(src, os.R_OK):
                    raise RuntimeError('Unreadable extra file %s' % src)

    def validate_builds_lists(self):
        if len(self.builds) < 1:
            raise RuntimeError('No builds files in config')
        distros = self.builds.keys()
        for distro, filename in self.builds.items():
            if not os.access(filename, os.R_OK):
                raise RuntimeError('Unreadable builds file %s' % filename)
            # Sanity-check the build NVRs for any mention of other_distros.
            with open(filename, 'r') as builds_fh:
                build_ids = [line.rstrip('\n') for line in builds_fh]
            other_distros = [d for d in distros if d != distro]
            for build_id in build_ids:
                for bad_distro in other_distros:
                    if bad_distro in build_id:
                        msg = '%s build %s in file %s' % (bad_distro, build_id,
                                                          filename)
                        raise RuntimeError(msg)

    @property
    def output_dir(self):
        """
        Use the same logic that pungi/compose.py uses in order come up with
        the name for the output directory. The name should be something
        like "Ceph-1.3-Ubuntu-20160922.t.0-x86_64" to match what
        Pungi creates.
        """
        if getattr(self, '_output_directory', None):
            return self._output_directory
        compose_date = time.strftime('%Y%m%d')
        compose_name = '{release_short}-{release_version}-{oslabel}-{arch}-{compose_date}{compose_type}.{compose_respin}'  # NOQA
        compose_type = COMPOSE_TYPE_MAP[self.compose_type]
        compose_respin = 0
        while 1:
            output_dir = os.path.join(self.target, compose_name.format(
                release_short=self.release_short,
                release_version=self.release_version,
                oslabel='Ubuntu',
                compose_date=compose_date,
                arch='x86_64',
                compose_type=compose_type,
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
        self.validate()

        if not os.path.isdir(self.cache_path):
            os.makedirs(self.cache_path)

        if not os.path.isdir(self.target):
            os.makedirs(self.target)

        # Make top-level output directory for this compose.
        os.mkdir(self.output_dir)

        # Top-level "dbg" directory, parallel to our output_dir.
        if self.include_dbg:
            dbg_dir = self.output_dir + '-dbg'
            os.mkdir(dbg_dir)

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

    @property
    def latest_name(self):
        tmpl = '{release_short}-{major_version}-{oslabel}-{arch}-latest'
        major_version = self.release_version.rsplit('.', 1)[0]
        return tmpl.format(
            release_short=self.release_short,
            major_version=major_version,
            oslabel='Ubuntu',
            arch='x86_64',
        )

    def symlink_latest(self):
        """ Create the "latest" symlink for this output_dir. """
        latest_path = os.path.join(self.target, self.latest_name)
        try:
            os.unlink(latest_path)
        except OSError as e:
            if e.errno != errno.ENOENT:
                log.error('Problem deleting "latest" symlink')
                raise SystemExit(e)
        os.symlink(os.path.relpath(self.output_dir, start=self.target),
                   latest_path)

    def run_distro(self, distro):
        """ Execute a compose for a distro. """

        # Read pkg mappings from Pungi-style comps XML.
        # (Assembles a master list of package names that we will need.)
        comps_file = self.comps[distro]
        comps = Comps()
        comps.parse_file(comps_file)

        # Query chacra for our list of builds.
        builds_file = self.builds[distro]  # builds .txt file for this distro
        builds = chacra.query(builds_file=builds_file,
                              chacra_url=self.chacra_url,
                              whitelist=comps.all_packages,
                              ssl_verify=self.chacra_ssl_verify)

        # Cache all our builds into self.cache_dir.
        gather.cache(builds=builds,
                     cache_dir=self.cache_path,
                     ssl_verify=self.chacra_ssl_verify)

        # Assign the builds' files to the correct groups, according to
        # comps.xml + variants.xml.

        dbg_binaries = set()

        for build in builds:
            # Assign each binary to its respective comps group(s).
            for binary in build.binaries:
                comps.assign_binary_to_groups(binary)
                # And track all dbg binaries.
                if comps.is_present(binary.dbg_parent):
                    dbg_binaries.add(binary)
            # Download all the source artifacts for this build and put them in
            # the "sources" directory.
            if self.include_sources:
                # Top-level "sources" directory, parallel to our output_dir.
                sources_dir = self.output_dir + '-sources'
                for source in build.sources:
                    # We've already downloaded to cache_path earlier, so this
                    # is just a copy operation now:
                    source.download(cache_dir=self.cache_path,
                                    dest_dir=sources_dir)

        variants = Variants()
        variants.parse_file(self.variants_file)

        # Create a repository for each variant.
        for variant_id, groups in variants.items():
            repo_path = os.path.join(self.output_dir, variant_id)
            binaries = set()
            for group_id in groups:
                to_add = comps.groups[group_id].binaries
                log.info('Adding %d binaries from comps ID %s to variant %s' %
                         (len(to_add), group_id, variant_id))
                binaries.update(to_add)
            self.create_repo(repo_path, distro, binaries)

        # Create dbg repository.
        if self.include_dbg:
            dbg_path = self.output_dir + '-dbg'
            self.create_repo(dbg_path, distro, dbg_binaries)

    def create_repo(self, repo_path, distro, binaries):
        """ Create a repository at repo_path. """
        # Top-level directory for this (variant) repository:
        if not os.path.isdir(repo_path):
            os.mkdir(repo_path)

        # Set up the reprepro configuration:
        log.info('Creating reprepro configuration for %s' % repo_path)
        conf_dir = os.path.join(repo_path, 'conf')
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

        for binary in binaries:
            # Add this binary to our variant's repo/directory:
            self.add_binary_to_repo(binary=binary,
                                    repo_path=repo_path,
                                    distro=distro)

    def add_binary_to_repo(self, binary, repo_path, distro):
        """ Add a binary (.deb) to a Debian repository. """
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
