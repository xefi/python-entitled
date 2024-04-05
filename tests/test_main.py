import pytest

from entitled.exceptions import AuthorizationException
from tests.test_policies import node_policy
from tests.test_rules import can_edit, is_admin, is_guest, is_member
from tests.testmodels import Node, Role, Tenant, User

org = Tenant(name="Eddy")
admin_user = User(name="mathias", tenant=org, roles=set([Role("admin")]))

normal_user = User(name="hugo", tenant=org)
guest_user = User(name="gautier", tenant=org, roles=set([Role("guest")]))


node = Node(name="root", owner=normal_user, tenant=org)


def test_rules():
    assert is_member(admin_user, org)
    assert is_member(guest_user, org)
    assert is_member(normal_user, org)

    assert is_guest(guest_user, org)
    assert is_admin(admin_user, org)
    assert not is_admin(guest_user, org)
    assert not is_guest(admin_user, org)

    assert can_edit(admin_user, node)
    assert can_edit(normal_user, node)


def test_policy():

    assert node_policy.allows(admin_user, "edit", node)
    assert node_policy.allows(normal_user, "edit", node)
    assert not node_policy.allows(guest_user, "edit", node)
    with pytest.raises(AuthorizationException):
        node_policy.authorize(guest_user, "edit", node)
