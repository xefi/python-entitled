from typing import Any
from entitled.old_policies import Policy
from tests.data.models import Resource, Tenant, User

tenant_policy = Policy[Tenant]("tenant")


@tenant_policy.rule("member")
def is_member(
    actor: User,
    resource: Tenant | type[Tenant],
    context: dict[str, Any] | None = None,
) -> bool:
    return actor.tenant == resource


@tenant_policy.rule("admin_role")
def has_admin_role(
    actor: User,
    resource: Tenant | type[Tenant],
    context: dict[str, Any] | None = None,
) -> bool:
    return is_member(actor, resource) and "admin" in actor.roles


resource_policy = Policy[Resource]("node")


@resource_policy.rule("edit")
def can_edit(
    actor: User,
    resource: Resource | type[Resource],
    context: dict[str, Any] | None = None,
) -> bool:
    return has_admin_role(actor, resource.tenant) or resource.owner == actor


@resource_policy.rule("view")
def can_view(
    actor: User,
    resource: Resource | type[Resource],
    context: dict[str, Any] | None = None,
) -> bool:
    return is_member(actor, resource.tenant)
