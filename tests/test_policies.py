import pytest

from entitled.exceptions import AuthorizationException
from entitled.policies import Policy
from entitled.rules import Rule
from tests.test_rules import can_edit, is_admin_on_node, is_member, is_owner
from tests.testmodels import Node, Role, Tenant, User

org = Tenant(name="Eddy")
admin_user = User(name="mathias", tenant=org, roles=set([Role("admin")]))

normal_user = User(name="hugo", tenant=org)
guest_user = User(name="gautier", tenant=org, roles=set([Role("guest")]))


node = Node(name="root", owner=normal_user, tenant=org)


@pytest.fixture
def testing_policy():
    return Policy[Node](
        {
            "edit": [can_edit],
            "delete": [is_owner | is_admin_on_node],
            "view": [
                Rule[User, Node](
                    "is_viewer",
                    lambda actor, resource, context: is_member(actor, resource.tenant),
                )
            ],
        }
    )


def test_policy_allows(testing_policy):
    assert testing_policy.allows(admin_user, "edit", node)
    assert testing_policy.allows(normal_user, "edit", node)
    assert not testing_policy.allows(guest_user, "edit", node)


def test_policy_authorize(testing_policy):
    with pytest.raises(AuthorizationException):
        testing_policy.authorize(guest_user, "edit", node)
