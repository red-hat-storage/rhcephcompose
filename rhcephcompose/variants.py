import xml.etree.ElementTree as ET


class Variants(dict):

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
