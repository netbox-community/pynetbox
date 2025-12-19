import pytest


@pytest.mark.usefixtures("init")
class BaseTest:
    app = "vpn"

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
