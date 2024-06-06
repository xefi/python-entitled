from typing import Any

import pytest

from entitled.rules import Rule, rule
from tests.fixtures.models import Tenant, User


class TestRuleCreation:
    def setup_method(self):
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
