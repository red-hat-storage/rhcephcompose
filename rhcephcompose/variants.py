import xml.etree.ElementTree as ET


class Variants(dict):
    """
    Class to parse and manage variants.

    Usage:

    variants = Variants()
    variants.parse_file(self.variants_file)
    for variant, groups in variants.items():
        print(variant)  # "Tools"
        for group in groups:
            print(group)  # "ceph-tools" (comps group)
    """

    def parse_file(self, filename):
        tree = ET.parse(filename)
        variants_root = tree.getroot()

        # Each variant can have one or more comps groups.
        for element in variants_root.getiterator('variant'):
            # For example, "<variant id="Installer" ... >"
            variant_id = element.attrib['id']
            # For example,
            # "<groups><group>ceph-installer</group></groups>"
            groups = []
            for group_element in element.find('groups').getiterator('group'):
                groups.append(group_element.text)
            self[variant_id] = groups
