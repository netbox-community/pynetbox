import pytest

from .base import BaseIntegrationTest


class BaseTest(BaseIntegrationTest):
    app = "users"


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
