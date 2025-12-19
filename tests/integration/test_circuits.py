import pytest


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


@pytest.fixture(scope="module")
def provider(api):
    ret = api.circuits.providers.create(name="test-provider", slug="test-provider")
    yield ret
    ret.delete()


@pytest.fixture(scope="module")
def circuit_type(api):
    ret = api.circuits.circuit_types.create(name="test-type", slug="test-type")
    yield ret
    ret.delete()


class TestProvider(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, provider):
        self._init_helper(
            request,
            provider,
            filter_kwargs={"name": "test-provider"},
            update_field="description",
            endpoint="providers",
        )


class TestCircuitType(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, circuit_type):
        self._init_helper(
            request,
            circuit_type,
            filter_kwargs={"name": "test-type"},
            update_field="description",
            endpoint="circuit_types",
        )


class TestCircuit(BaseTest):
    @pytest.fixture(scope="class")
    def circuit(self, api, provider, circuit_type):
        ret = api.circuits.circuits.create(
            cid="test-circuit-123", provider=provider.id, type=circuit_type.id
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, circuit):
        self._init_helper(
            request,
            circuit,
            filter_kwargs={"cid": "test-circuit-123"},
            update_field="description",
            endpoint="circuits",
            str_repr="test-circuit-123",
        )
