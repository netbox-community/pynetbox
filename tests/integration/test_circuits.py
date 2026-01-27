import pytest



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


@pytest.fixture(scope="module")
def provider_network(api, provider):
    provider_network = api.circuits.provider_networks.create(
        name="test-provider-network", provider=provider.id
    )
    yield provider_network
    provider_network.delete()


@pytest.fixture(scope="module")
def virtual_circuit_type(api):
    virtual_circuit_type = api.circuits.virtual_circuit_types.create(
        name="test-virtual-circuit-type", slug="test-virtual-circuit-type"
    )
    yield virtual_circuit_type
    virtual_circuit_type.delete()


@pytest.fixture(scope="module")
def virtual_circuit(api, provider_network, virtual_circuit_type):
    virtual_circuit = api.circuits.virtual_circuits.create(
        cid="TEST-VCIRCUIT-001",
        provider_network=provider_network.id,
        type=virtual_circuit_type.id,
    )
    yield virtual_circuit
    virtual_circuit.delete()


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
    def site_b(self, api):
        site_b = api.dcim.sites.create(name="test-site-b", slug="test-site-b")
        yield site_b
        site_b.delete()

    @pytest.fixture(scope="class")
    def circuit_termination_a(self, api, circuit, site):
        ret = api.circuits.circuit_terminations.create(
            circuit=circuit.id,
            site=site.id,
            term_side="A",
            termination_type="dcim.site",
            termination_id=site.id,
        )
        yield ret

    @pytest.fixture(scope="class")
    def circuit_termination_b(self, api, circuit, site_b):
        ret = api.circuits.circuit_terminations.create(
            circuit=circuit.id,
            site=site_b.id,
            term_side="Z",
            termination_type="dcim.site",
            termination_id=site_b.id,
        )
        yield ret

    @pytest.fixture(scope="class")
    def init(
        self,
        request,
        circuit_termination_a,
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
        assert isinstance(paths_result, list)
        # Circuit terminations may have paths if connected through patch panels
        # For this test, we just verify the method works and returns correct structure
        if paths_result:
            for path in paths_result:
                assert "origin" in path
                assert "destination" in path
                assert "path" in path
                assert isinstance(path["path"], list)


class TestVirtualCircuit(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, virtual_circuit):
        self._init_helper(
            request,
            virtual_circuit,
            filter_kwargs={"cid": virtual_circuit.cid},
            update_field="description",
            endpoint="virtual_circuits",
            str_repr=virtual_circuit.cid,
        )


class TestVirtualCircuitTermination(BaseTest):
    @pytest.fixture(scope="class")
    def device(self, api, site, device_type, role):
        from tests.integration.conftest import create_device

        device = create_device(api, site, device_type, role, "test-vcircuit-device")
        yield device
        device.delete()

    @pytest.fixture(scope="class")
    def interface_a(self, api, device):
        ret = api.dcim.interfaces.create(
            name="vlan100", type="virtual", device=device.id
        )
        yield ret

    @pytest.fixture(scope="class")
    def interface_b(self, api, device):
        ret = api.dcim.interfaces.create(
            name="vlan200", type="virtual", device=device.id
        )
        yield ret

    @pytest.fixture(scope="class")
    def virtual_circuit_termination_a(self, api, virtual_circuit, interface_a):
        ret = api.circuits.virtual_circuit_terminations.create(
            virtual_circuit=virtual_circuit.id, role="hub", interface=interface_a.id
        )
        yield ret

    @pytest.fixture(scope="class")
    def virtual_circuit_termination_b(self, api, virtual_circuit, interface_b):
        ret = api.circuits.virtual_circuit_terminations.create(
            virtual_circuit=virtual_circuit.id, role="spoke", interface=interface_b.id
        )
        yield ret

    @pytest.fixture(scope="class")
    def init(
        self,
        request,
        virtual_circuit_termination_a,
    ):
        self._init_helper(
            request,
            virtual_circuit_termination_a,
            filter_kwargs={
                "virtual_circuit_id": virtual_circuit_termination_a.virtual_circuit.id
            },
            endpoint="virtual_circuit_terminations",
            str_repr=virtual_circuit_termination_a.virtual_circuit.cid,
        )

    def test_virtual_circuit_termination_paths(self, virtual_circuit_termination_a):
        paths_result = virtual_circuit_termination_a.paths()
        assert isinstance(paths_result, list)
        # Virtual circuit terminations may have paths if they traverse physical infrastructure
        # For this test, we just verify the method works and returns correct structure
        if paths_result:
            for path in paths_result:
                assert "origin" in path
                assert "destination" in path
                assert "path" in path
                assert isinstance(path["path"], list)
