import pytest
from packaging import version

from .base import BaseIntegrationTest


class BaseTest(BaseIntegrationTest):
    app = "ipam"


@pytest.fixture(scope="module")
def rir(api, site):
    ret = api.ipam.rirs.create(
        name="ministry-of-silly-walks", slug="ministry-of-silly-walks"
    )
    yield ret
    ret.delete()


class TestRIR(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, rir, nb_version):
        self._init_helper(
            request,
            rir,
            filter_kwargs={"name": "ministry-of-silly-walks"},
            update_field="description" if nb_version >= version.parse("2.8") else None,
            endpoint="rirs",
        )


class TestAggregate(BaseTest):
    @pytest.fixture(scope="class")
    def aggregate(self, api, rir):
        ret = api.ipam.aggregates.create(prefix="192.0.2.0/24", rir=rir.id)
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, aggregate):
        self._init_helper(
            request,
            aggregate,
            filter_kwargs={"prefix": "192.0.2.0/24"},
            update_field="description",
            endpoint="aggregates",
        )


class TestPrefix(BaseTest):
    @pytest.fixture(scope="class")
    def prefix(self, api):
        ret = api.ipam.prefixes.create(prefix="192.0.2.0/24")
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, prefix):
        self._init_helper(
            request,
            prefix,
            filter_kwargs={"prefix": "192.0.2.0/24"},
            update_field="description",
            endpoint="prefixes",
        )


class TestIpAddress(BaseTest):
    @pytest.fixture(scope="class")
    def ip(self, api):
        ret = api.ipam.ip_addresses.create(address="192.0.2.1/24")
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, ip):
        self._init_helper(
            request,
            ip,
            filter_kwargs={"q": "192.0.2.1/24"},
            update_field="description",
            endpoint="ip_addresses",
        )


class TestRole(BaseTest):
    @pytest.fixture(scope="class")
    def role(self, api):
        ret = api.ipam.roles.create(name="test-role", slug="test-role")
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, role):
        self._init_helper(
            request,
            role,
            filter_kwargs={"name": "test-role"},
            update_field="description",
            endpoint="roles",
        )


class TestVlan(BaseTest):
    @pytest.fixture(scope="class")
    def vlan(self, api):
        ret = api.ipam.vlans.create(vid=123, name="test-vlan")
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, vlan):
        self._init_helper(
            request,
            vlan,
            filter_kwargs={"name": "test-vlan"},
            update_field="description",
            endpoint="vlans",
        )


class TestVRF(BaseTest):
    @pytest.fixture(scope="class")
    def vrf(self, api):
        ret = api.ipam.vrfs.create(name="test-vrf", rd="192.0.2.1:1234")
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, vrf):
        self._init_helper(
            request,
            vrf,
            filter_kwargs={"name": "test-vrf"},
            update_field="description",
            endpoint="vrfs",
        )
