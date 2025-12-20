import pytest

from .base import BaseIntegrationTest


class BaseTest(BaseIntegrationTest):
    app = "virtualization"


@pytest.fixture(scope="module")
def cluster_type(api):
    ret = api.virtualization.cluster_types.create(
        name="test-cluster-type", slug="test-cluster-type"
    )
    yield ret
    ret.delete()


@pytest.fixture(scope="module")
def cluster(api, cluster_type):
    ret = api.virtualization.clusters.create(name="test-cluster", type=cluster_type.id)
    yield ret
    ret.delete()


class TestClusterType(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, cluster_type):
        self._init_helper(
            request,
            cluster_type,
            filter_kwargs={"name": "test-cluster-type"},
            update_field="description",
            endpoint="cluster_types",
        )


class TestCluster(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, cluster):
        self._init_helper(
            request,
            cluster,
            filter_kwargs={"name": "test-cluster"},
            update_field="description",
            endpoint="clusters",
        )


class TestVirtualMachine(BaseTest):
    @pytest.fixture(scope="class")
    def virtual_machine(self, api, cluster):
        ret = api.virtualization.virtual_machines.create(
            name="test-vm", cluster=cluster.id
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, virtual_machine):
        self._init_helper(
            request,
            virtual_machine,
            filter_kwargs={"name": "test-vm"},
            update_field="description",
            endpoint="virtual_machines",
        )
