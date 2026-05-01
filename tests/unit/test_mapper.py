import unittest

from pynetbox.models.mapper import CONTENT_TYPE_MAPPER
from pynetbox.models.virtualization import VirtualMachineTypes


class ContentTypeMapperTestCase(unittest.TestCase):
    def test_cable_bundle_registered(self):
        self.assertIn("dcim.cablebundle", CONTENT_TYPE_MAPPER)

    def test_rack_group_registered(self):
        self.assertIn("dcim.rackgroup", CONTENT_TYPE_MAPPER)

    def test_virtual_machine_type_registered(self):
        self.assertIn("virtualization.virtualmachinetype", CONTENT_TYPE_MAPPER)
        self.assertIs(
            CONTENT_TYPE_MAPPER["virtualization.virtualmachinetype"], VirtualMachineTypes
        )
