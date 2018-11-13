import os
import productmd.composeinfo

"""
Write a composeinfo.json file with productmd.
"""


def write_composeinfo(compose):
    ci = productmd.composeinfo.ComposeInfo()

    ci.compose.id = compose.id
    ci.compose.type = compose.compose_type
    ci.compose.date = compose.date
    ci.compose.respin = compose.respin
    # TODO: support "label", for marking "Beta".

    ci.release.name = 'Red Hat Ceph'
    ci.release.short = compose.release_short
    ci.release.version = compose.release_version
    ci.release.is_layered = True
    ci.release.type = 'ga'
    ci.release.internal = False

    ci.base_product.name = 'Ubuntu'
    ci.base_product.version = 'ubuntu'  # could be multiple here
    ci.base_product.short = 'ubuntu'
    ci.base_product.type = 'ga'

    # TODO: add variants here, like:
    # var = productmd.composeinfo.Variant(ci)
    # var.id = 'Tools'
    # var.uid = 'Tools'
    # var.name = 'Ceph Tools'
    # var.type = 'variant'
    # var.arches = ['x86_64']
    # ci.variants.add(var)

    path = os.path.join(compose.output_dir, 'metadata', 'composeinfo.json')
    ci.dump(path)
