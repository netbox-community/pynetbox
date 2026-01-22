import pytest

import pynetbox


@pytest.fixture(scope="module")
def provider(api):
    provider = api.circuits.providers.create(name="test-provider", slug="test-provider")
    yield provider
    provider.delete()


@pytest.fixture(scope="module")
def circuit_type(api):
    circuit_type = api.circuits.circuit_types.create(
        name="test-circuit-type", slug="test-circuit-type"
    )
    yield circuit_type
    circuit_type.delete()


@pytest.fixture(scope="module")
def circuit(api, provider, circuit_type):
    circuit = api.circuits.circuits.create(
        cid="TEST-CIRCUIT-001", provider=provider.id, type=circuit_type.id
    )
    yield circuit
    circuit.delete()


@pytest.mark.usefixtures("init")
class BaseTest:
    app = "circuits"

    def _init_helper(
        self,
        request,
        fixture,
        update_field=None,
        filter_kwargs=None,
        endpoint=None,
        str_repr=None,
    ):
        request.cls.endpoint = endpoint
        request.cls.fixture = fixture
        request.cls.update_field = update_field
        request.cls.filter_kwargs = filter_kwargs
        request.cls.str_repr = str_repr

    def test_create(self):
        assert self.fixture

    def test_str(self):
        if self.str_repr:
            test = str(self.fixture)
            assert test == self.str_repr

    def test_update_fixture(self):
        if self.update_field:
            setattr(self.fixture, self.update_field, "Test Value")
            assert self.fixture.save()

    def test_get_fixture_by_id(self, api):
        test = getattr(getattr(api, self.app), self.endpoint).get(self.fixture.id)
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"

    def test_get_fixture_by_kwarg(self, api):
        test = getattr(getattr(api, self.app), self.endpoint).get(**self.filter_kwargs)
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"

    def test_filter_fixture(self, api):
        test = list(
            getattr(getattr(api, self.app), self.endpoint).filter(**self.filter_kwargs)
        )[0]
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"


class TestCircuit(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, circuit):
        self._init_helper(
            request,
            circuit,
            filter_kwargs={"cid": circuit.cid},
            update_field="description",
            endpoint="circuits",
            str_repr=circuit.cid,
        )


class TestCircuitTermination(BaseTest):
    @pytest.fixture(scope="class")
    def device(self, api, site, device_type, role):
        from .conftest import create_device

        device = create_device(api, site, device_type, role, "test-circuit-device")
        yield device
        device.delete()

    @pytest.fixture(scope="class")
    def interface_a(self, api, device):
        ret = api.dcim.interfaces.create(
            name="GigabitEthernet0/0", type="1000base-t", device=device.id
        )
        yield ret

    @pytest.fixture(scope="class")
    def interface_b(self, api, device):
        ret = api.dcim.interfaces.create(
            name="GigabitEthernet0/1", type="1000base-t", device=device.id
        )
        yield ret

    @pytest.fixture(scope="class")
    def circuit_termination_a(self, api, circuit, site):
        ret = api.circuits.circuit_terminations.create(
            circuit=circuit.id, site=site.id, term_side="A"
        )
        yield ret

    @pytest.fixture(scope="class")
    def circuit_termination_b(self, api, circuit, site):
        ret = api.circuits.circuit_terminations.create(
            circuit=circuit.id, site=site.id, term_side="Z"
        )
        yield ret

    @pytest.fixture(scope="class")
    def cable_a(self, api, circuit_termination_a, interface_a):
        ret = api.dcim.cables.create(
            a_terminations=[
                {
                    "object_type": "circuits.circuittermination",
                    "object_id": circuit_termination_a.id,
                },
            ],
            b_terminations=[
                {"object_type": "dcim.interface", "object_id": interface_a.id},
            ],
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def cable_b(self, api, circuit_termination_b, interface_b):
        ret = api.dcim.cables.create(
            a_terminations=[
                {
                    "object_type": "circuits.circuittermination",
                    "object_id": circuit_termination_b.id,
                },
            ],
            b_terminations=[
                {"object_type": "dcim.interface", "object_id": interface_b.id},
            ],
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(
        self,
        request,
        circuit_termination_a,
        cable_a,
        cable_b,
    ):
        self._init_helper(
            request,
            circuit_termination_a,
            filter_kwargs={"circuit_id": circuit_termination_a.circuit.id},
            endpoint="circuit_terminations",
            str_repr=circuit_termination_a.circuit.cid,
        )

    def test_circuit_termination_paths(self, circuit_termination_a):
        paths_result = circuit_termination_a.paths()
        assert paths_result
        assert isinstance(paths_result, list)
        # Each path should have origin, destination, and path keys
        for path in paths_result:
            assert "origin" in path
            assert "destination" in path
            assert "path" in path
            assert isinstance(path["path"], list)
