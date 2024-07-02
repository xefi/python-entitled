from pathlib import Path

import pytest
from _pytest.pytester import pytester

from entitled import exceptions
from entitled.client import Client
from entitled.rules import Rule
from tests.fixtures.models import Resource, Tenant, User
from tests.fixtures.policies import resource_policy, tenant_policy


class TestClientCreation:
    def teardown_method(self):
        Rule.clear_registry()

    def test_create_client(self):
        client = Client()
        assert client._load_path is None
        assert client._policy_registrar == {}

    def test_create_client_with_loadpath(self):
        client = Client(base_path="tests/fixtures")

        assert client._load_path == Path("tests/fixtures")
        assert len(client._policy_registrar.items()) == 2


class TestClientDecision:

    def teardown_method(self):
        Rule.clear_registry()

    def test_grants(self):
        client = Client(base_path="tests/fixtures")
        tenant1 = Tenant("tenant1")
        tenant2 = Tenant("tenant2")
        user1 = User("user1", tenant1, set(["user"]))
        user2 = User("user2", tenant2, set(["user"]))
        resource1 = Resource("R1", user1, tenant1)

        u1_grants = client.grants(user1, resource1)
        u2_grants = client.grants(user2, resource1)
        assert "view" in u1_grants and "edit" in u1_grants
        assert u1_grants["view"] and u1_grants["edit"]
        assert "view" in u2_grants and "edit" in u2_grants
        assert not u2_grants["view"] and not u2_grants["edit"]

    def test_allows(self):
        client = Client(base_path="tests/fixtures")
        tenant1 = Tenant("tenant1")
        tenant2 = Tenant("tenant2")
        user1 = User("user1", tenant1, set(["user"]))
        user2 = User("user2", tenant2, set(["user"]))
        resource1 = Resource("R1", user1, tenant1)

        assert client.allows("edit", user1, resource1)
        assert not client.allows("edit", user2, resource1)
        assert not client.allows("move", user2, resource1)

    def test_authorize(self):
        client = Client(base_path="tests/fixtures")
        tenant1 = Tenant("tenant1")
        tenant2 = Tenant("tenant2")
        user1 = User("user1", tenant1, set(["user"]))
        user2 = User("user2", tenant2, set(["user"]))
        resource1 = Resource("R1", user1, tenant1)

        assert client.authorize("edit", user1, resource1)
        with pytest.raises(exceptions.AuthorizationException):
            client.authorize("edit", user2, resource1)
        with pytest.raises(exceptions.UndefinedAction):
            client.authorize("move", user2, resource1)
