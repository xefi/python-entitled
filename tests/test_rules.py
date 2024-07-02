from typing import Any

import pytest

from entitled import exceptions
from entitled.rules import Rule, rule
from tests.fixtures.models import Tenant, User


class TestRuleCreation:
    def teardown_method(self):
        Rule.clear_registry()

    def test_create_with_constructor(self):
        def is_member(
            actor: User, resource: Tenant, context: dict[str, Any] | None = None
        ) -> bool:
            return actor.tenant == resource

        new_rule = Rule[Tenant]("is_member", is_member)

        assert Rule._registry["is_member"] == new_rule

    def test_create_with_decorator(self):
        @rule("is_member")
        def is_member(
            actor: User, resource: Tenant, context: dict[str, Any] | None = None
        ) -> bool:
            return actor.tenant == resource

        assert Rule._registry["is_member"].name == "is_member"

    def test_create_with_same_name(self):
        @rule("is_member")
        def is_member(
            actor: User, resource: Tenant, context: dict[str, Any] | None = None
        ) -> bool:
            return actor.tenant == resource

        with pytest.raises(ValueError):

            @rule("is_member")
            def another_rule(
                actor: User, resource: Tenant, context: dict[str, Any] | None = None
            ) -> bool:
                return True


class TestReadRules:
    def setup_method(self):
        @rule("is_member")
        def is_member(
            actor: User, resource: Tenant, context: dict[str, Any] | None = None
        ) -> bool:
            return actor.tenant == resource

    def teardown_method(self):
        Rule.clear_registry()

    def test_fetch_registered_rule(self):
        res = Rule.get_rule("is_member")
        assert res is not None
        assert res.name == "is_member"

    def test_fetch_non_registered_rule(self):
        res = Rule.get_rule("is_admin")
        assert res is None


class TestRuleCalls:
    def setup_method(self):
        @rule("is_member")
        def is_member(
            actor: User, resource: Tenant, context: dict[str, Any] | None = None
        ) -> bool:
            return actor.tenant == resource

    def teardown_method(self):
        Rule.clear_registry()

    def test_rule_call(self):
        tenant = Tenant("test_tenant")
        res = Rule.get_rule("is_member")
        assert res is not None
        assert res(User("test_user", tenant, set()), tenant)

    def test_authorize(self):
        tenant = Tenant("test_tenant")
        test_user = User("test_user", tenant, set())
        res = Rule.get_rule("is_member")
        assert res is not None
        assert res.authorize(test_user, tenant)

        new_tenant = Tenant("other_tenant")
        with pytest.raises(exceptions.AuthorizationException):
            res.authorize(test_user, new_tenant)

    def test_allows(self):
        tenant = Tenant("test_tenant")
        test_user = User("test_user", tenant, set())
        res = Rule.get_rule("is_member")
        assert res is not None
        assert res.allows(test_user, tenant)

        new_tenant = Tenant("other_tenant")
        assert not res.allows(test_user, new_tenant)
