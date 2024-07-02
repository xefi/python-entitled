from entitled import policies
from entitled.policies import Policy
from entitled.rules import Rule
from tests.fixtures.models import Tenant, User


class TestPolicyCreation:
    def teardown_method(self):
        Rule.clear_registry()

    def test_policy_creation(self):
        policy = Policy("my_policy")
        assert policy.label == "my_policy"
        assert policy._registry == {}

    def test_register_rule_decorator(self):
        policy = Policy[Tenant]("my_policy")

        @policy.rule("is_member")
        def is_member(
            actor: User, resource: Tenant, context: dict | None = None
        ) -> bool:
            return actor.tenant == resource

        assert policy.label == "my_policy"
        assert policy._registry["is_member"][0].name == "my_policy:is_member"
        rule = Rule.get_rule("my_policy:is_member")
        assert rule is not None
        assert not rule.name == "is_member"

    def test_register_rule_function(self):
        policy = Policy[Tenant]("my_policy")

        @policy.rule("is_member")
        def is_member(
            actor: User, resource: Tenant, context: dict | None = None
        ) -> bool:
            return actor.tenant == resource

        assert policy.label == "my_policy"
        assert policy._registry["is_member"][0].name == "my_policy:is_member"
        rule = Rule.get_rule("my_policy:is_member")
        assert rule is not None
        assert not rule.name == "is_member"


class TestPolicyAuthorization:
    def teardown_method(self):
        Rule.clear_registry()

    def test_list_grants(self):
        policy = Policy[Tenant]("tenant")

        @policy.rule("is_member")
        def is_member(
            actor: User, resource: Tenant, context: dict | None = None
        ) -> bool:
            return actor.tenant == resource

        @policy.rule("has_admin_role")
        def has_admin_role(
            actor: User, resource: Tenant, context: dict | None = None
        ) -> bool:
            return "admin" in actor.roles

        @policy.rule("is_tenant_admin")
        def is_tenant_admin(
            actor: User, resource: Tenant, context: dict | None = None
        ) -> bool:
            return is_member(actor, resource, context) and has_admin_role(
                actor, resource, context
            )

        tenant1 = Tenant(name="tenant1")
        admin_role = "admin"
        guest_role = "user"
        user1 = User(name="user1", tenant=tenant1, roles=set([admin_role]))
        user2 = User(name="user2", tenant=tenant1, roles=set([guest_role]))

        assert policy.grants(user1, tenant1)["is_member"]
        assert policy.grants(user2, tenant1)["is_member"]
        assert policy.grants(user1, tenant1)["is_tenant_admin"]
        assert not policy.grants(user2, tenant1)["is_tenant_admin"]
