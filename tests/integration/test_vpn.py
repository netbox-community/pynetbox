import pytest

from .base import BaseIntegrationTest


class BaseTest(BaseIntegrationTest):
    app = "vpn"


class TestTunnel(BaseTest):
    @pytest.fixture(scope="class")
    def tunnel(self, api):
        ret = api.vpn.tunnels.create(
            name="test-tunnel",
            encapsulation="ipsec-transport",
            status="active",
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, tunnel):
        self._init_helper(
            request,
            tunnel,
            filter_kwargs={"name": "test-tunnel"},
            update_field="description",
            endpoint="tunnels",
        )


class TestTunnelGroup(BaseTest):
    @pytest.fixture(scope="class")
    def tunnel_group(self, api):
        ret = api.vpn.tunnel_groups.create(
            name="test-tunnel-group", slug="test-tunnel-group"
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, tunnel_group):
        self._init_helper(
            request,
            tunnel_group,
            filter_kwargs={"name": "test-tunnel-group"},
            update_field="description",
            endpoint="tunnel_groups",
        )


class TestIKEProposal(BaseTest):
    @pytest.fixture(scope="class")
    def ike_proposal(self, api):
        ret = api.vpn.ike_proposals.create(
            name="test-ike-proposal",
            authentication_method="preshared-keys",
            encryption_algorithm="aes-128-cbc",
            authentication_algorithm="hmac-sha1",
            group=14,
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, ike_proposal):
        self._init_helper(
            request,
            ike_proposal,
            filter_kwargs={"name": "test-ike-proposal"},
            update_field="description",
            endpoint="ike_proposals",
        )
