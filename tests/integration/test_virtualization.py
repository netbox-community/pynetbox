import pytest


@pytest.mark.usefixtures("init")
class BaseTest:
    app = "virtualization"

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
