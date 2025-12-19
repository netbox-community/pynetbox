import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.circuits

HEADERS = {"accept": "application/json"}


class CircuitsTests(Generic.Tests):
    app = "circuits"


class CircuitsTestCase(CircuitsTests):
    name = "circuits"

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="circuits/circuit.json"),
    )
    def test_repr(self, _):
        test = nb.circuits.get(1)
        self.assertEqual(str(test), "123456")


class ProviderTestCase(CircuitsTests):
    name = "providers"


class CircuitTypeTestCase(CircuitsTests):
    name = "circuit_types"


class CircuitTerminationsTestCase(CircuitsTests):
    name = "circuit_terminations"

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="circuits/circuit_termination.json"),
    )
    def test_repr(self, _):
        test = nb.circuit_terminations.get(1)
        self.assertEqual(str(test), "123456")


class CircuitGroupsTestCase(CircuitsTests):
    name = "circuit_groups"


class CircuitGroupAssignmentsTestCase(CircuitsTests):
    name = "circuit_group_assignments"


class ProviderAccountsTestCase(CircuitsTests):
    name = "provider_accounts"


class ProviderNetworksTestCase(CircuitsTests):
    name = "provider_networks"


class VirtualCircuitsTestCase(CircuitsTests):
    name = "virtual_circuits"


class VirtualCircuitTypesTestCase(CircuitsTests):
    name = "virtual_circuit_types"


class VirtualCircuitTerminationsTestCase(CircuitsTests):
    name = "virtual_circuit_terminations"
