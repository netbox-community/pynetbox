import pytest

from .base import BaseIntegrationTest


class BaseTest(BaseIntegrationTest):
    app = "circuits"


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
