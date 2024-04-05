from entitled.roles import Role
from entitled.rules import Rule
from tests.testmodels import Node, Tenant, User

is_member = Rule[User, Tenant](
    "is_member", lambda actor, resource, context: actor.tenant == resource
)

is_admin = Rule[User, Tenant](
    "is_admin",
    lambda actor, resource, context: is_member(actor, resource)
    and Role("admin") in actor.roles,
)

is_guest = Rule[User, Tenant](
    "is_guest",
    lambda actor, resource, context: is_member(actor, resource)
    and Role("guest") in actor.roles,
)

has_role = Rule[User, Tenant](
    "has_role",
    lambda actor, resource, context: "role" in context.keys()
    and is_member(actor, resource)
    and Role(context["role"]) in actor.roles,
)

can_edit = Rule[User, Node](
    "can_edit",
    lambda actor, resource, context: is_admin(actor, resource.tenant)
    or (is_member(actor, resource.tenant) and resource.owner == actor),
)

is_admin_on_node = Rule[User, Node](
    "is_admin_on_node",
    lambda actor, resource, context: is_admin(actor, resource.tenant),
)

is_owner = Rule[User, Node](
    "is_owner",
    lambda actor, resource, context: is_member(actor, resource.tenant)
    and resource.owner == actor,
)
