import os
from rhcephcompose.metadata import composeinfo
from rhcephcompose.metadata import debs


def write(compose, build_metadata):
    """
    Write all the metadata for this compose and its builds.
    """
    directory = os.path.join(compose.output_dir, 'metadata')
    if not os.path.isdir(directory):
        os.mkdir(directory)
    composeinfo.write_composeinfo(compose)
    debs.write_debs(directory, build_metadata)
