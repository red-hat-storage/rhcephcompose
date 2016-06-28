import xml.etree.ElementTree as ET

from rhcephcompose.log import log


class CompsGroup(list):
    """ A list of packages in a comps <group>. """
    def __init__(self, group_id=None):
        self.group_id = group_id
        self.binaries = []


class Comps(object):

    def __init__(self):
        self.all_packages = []
        self.groups = {}

    def parse_file(self, filename):
        tree = ET.parse(filename)
        comps_root = tree.getroot()

        for element in comps_root.getiterator('group'):
            group = CompsGroup()
            for setting in element:
                if setting.tag == 'id':
                    group.group_id = setting.text
                if setting.tag == 'packagelist':
                    for pkg in setting:
                        # Populate our CompsGroup
                        group.append(pkg.text)
                        # Also store this in the "all_packages" list
                        self.all_packages.append(pkg.text)
            if not group.group_id:
                log.error('No group <id> found in <group>')
                exit(1)
            self.groups[group.group_id] = group

    def assign_binary_to_groups(self, binary):
        for group in self.groups.values():
            if binary.name in group:
                msg = 'binary %s is in group %s, appending.'
                log.info(msg % (binary.name, group.group_id))
                group.binaries.append(binary)
