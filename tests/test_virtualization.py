import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.virtualization

HEADERS = {"accept": "application/json"}


class VirtualizationBase(Generic.Tests):
    __test__ = False  # Prevent pytest from discovering this as a test class
    app = "virtualization"


class ClusterTypesTestCase(VirtualizationBase):
    name = "cluster_types"


class ClusterGroupsTestCase(VirtualizationBase):
    name = "cluster_groups"


class ClustersTestCase(VirtualizationBase):
    name = "clusters"


class VirtualMachinesTestCase(VirtualizationBase):
    name = "virtual_machines"


class VirtualDisksTestCase(VirtualizationBase):
    name = "virtual_disks"


class InterfacesTestCase(VirtualizationBase):
    name = "interfaces"
