import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.virtualization

HEADERS = {"accept": "application/json"}


class VirtualizationTests(Generic.Tests):
    app = "virtualization"


class ClusterTypesTestCase(VirtualizationTests):
    name = "cluster_types"


class ClusterGroupsTestCase(VirtualizationTests):
    name = "cluster_groups"


class ClustersTestCase(VirtualizationTests):
    name = "clusters"


class VirtualMachinesTestCase(VirtualizationTests):
    name = "virtual_machines"


class VirtualDisksTestCase(VirtualizationTests):
    name = "virtual_disks"


class InterfacesTestCase(VirtualizationTests):
    name = "interfaces"
