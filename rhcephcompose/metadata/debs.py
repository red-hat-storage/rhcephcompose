import json
import os


"""
Write a debs.json file. Similar concept to productmd's rpms.json, but simpler.
"""


HEADER = {
    'type': 'rhcephcompose.debs',
    'version': '1.0',
}


def write_debs(directory, build_metadata):
    """
    :param str directory: "metadata" directory
    :param dict build_metadata: distro/build information
    """
    debs = {}
    for distro, builds in build_metadata.items():
        debs[distro] = [b.build_id for b in builds]
    data = {
        'header': HEADER,
        'payload': {'debs': debs}
    }
    path = os.path.join(directory, 'debs.json')
    with open(path, 'w') as f:
        json.dump(data, f)
