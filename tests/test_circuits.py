from unittest.mock import patch

import pynetbox

from .generic import Generic
from .util import Response

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.circuits

HEADERS = {"accept": "application/json"}


class CircuitsBase(Generic.Tests):
    __test__ = False  # Prevent pytest from discovering this as a test class
    app = "circuits"


class CircuitsTestCase(CircuitsBase):
    name = "circuits"

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="circuits/circuit.json"),
    )
    def test_repr(self, _):
        test = nb.circuits.get(1)
        self.assertEqual(str(test), "123456")


class ProviderTestCase(CircuitsBase):
    name = "providers"


class CircuitTypeTestCase(CircuitsBase):
    name = "circuit_types"


class CircuitTerminationsTestCase(CircuitsBase):
    name = "circuit_terminations"

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="circuits/circuit_termination.json"),
    )
    def test_repr(self, _):
        test = nb.circuit_terminations.get(1)
        self.assertEqual(str(test), "123456")


class CircuitGroupsTestCase(CircuitsBase):
    name = "circuit_groups"


class CircuitGroupAssignmentsTestCase(CircuitsBase):
    name = "circuit_group_assignments"


class ProviderAccountsTestCase(CircuitsBase):
    name = "provider_accounts"


class ProviderNetworksTestCase(CircuitsBase):
    name = "provider_networks"


class VirtualCircuitsTestCase(CircuitsBase):
    name = "virtual_circuits"


class VirtualCircuitTypesTestCase(CircuitsBase):
    name = "virtual_circuit_types"


class VirtualCircuitTerminationsTestCase(CircuitsBase):
    name = "virtual_circuit_terminations"
