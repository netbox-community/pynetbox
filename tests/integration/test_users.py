import pytest


@pytest.mark.usefixtures("init")
class BaseTest:
    app = "users"

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


class TestGroup(BaseTest):
    @pytest.fixture(scope="class")
    def group(self, api):
        ret = api.users.groups.create(name="test-group")
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, group):
        self._init_helper(
            request,
            group,
            filter_kwargs={"name": "test-group"},
            update_field="description",
            endpoint="groups",
        )


class TestUser(BaseTest):
    @pytest.fixture(scope="class")
    def user(self, api):
        ret = api.users.users.create(username="testuser123", password="TestPassword123")
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, user):
        self._init_helper(
            request,
            user,
            filter_kwargs={"username": "testuser123"},
            endpoint="users",
            str_repr="testuser123",
        )


@pytest.fixture(scope="module")
def test_user(api):
    ret = api.users.users.create(
        username="testuser-for-token", password="TestPassword123"
    )
    yield ret
    ret.delete()


class TestToken(BaseTest):
    @pytest.fixture(scope="class")
    def token(self, api, test_user):
        ret = api.users.tokens.create(user=test_user.id)
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, token):
        self._init_helper(
            request,
            token,
            filter_kwargs={"id": token.id},
            endpoint="tokens",
        )
