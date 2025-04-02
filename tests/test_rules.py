import pytest

from entitled.exceptions import AuthorizationException
from entitled.response import Err, Ok, Response
from entitled.rules import Rule
from tests.data.factories import TenantFactory, UserFactory
from tests.data.models import User, Tenant

pytestmark = pytest.mark.anyio


async def is_member(
    actor: User,
    resource: Tenant,
) -> bool:
    return actor.tenant == resource


async def is_owner(
    actor: User,
    resource: Tenant,
) -> Response:
    return Ok() if resource.owner == actor else Err("Not owner on the tenant")


def test_define():
    rule = Rule[User]("is_member", is_member)
    assert rule.callable == is_member


async def test_allows():
    tenant1 = TenantFactory()
    tenant2 = TenantFactory()
    user1 = UserFactory(tenant=tenant1)
    user2 = UserFactory(tenant=tenant2)
    tenant2.owner = user2

    rule1 = Rule[User]("is_member", is_member)
    rule2 = Rule[User]("is_owner", is_owner)

    assert await rule1.allows(user1, tenant1)
    assert not await rule1.denies(user1, tenant1)
    assert not await rule1.allows(user2, tenant1)
    assert await rule1.denies(user2, tenant1)

    assert not await rule2.allows(user1, tenant2)
    assert await rule2.denies(user1, tenant2)
    assert await rule2.allows(user2, tenant2)
    assert not await rule2.denies(user2, tenant2)


async def test_authorize():
    tenant1 = TenantFactory()
    tenant2 = TenantFactory()
    user1 = UserFactory(tenant=tenant1)
    user2 = UserFactory(tenant=tenant2)
    tenant2.owner = user2

    rule1 = Rule[User]("is_member", is_member)
    rule2 = Rule[User]("is_owner", is_owner)

    assert await rule1.authorize(user1, tenant1)
    with pytest.raises(AuthorizationException):
        _ = await rule1.authorize(user2, tenant1)
    with pytest.raises(AuthorizationException):
        _ = await rule2.authorize(user1, tenant2)
    assert await rule2.authorize(user2, tenant2)


async def test_inspect():
    tenant1 = TenantFactory()
    tenant2 = TenantFactory()
    user1 = UserFactory(tenant=tenant1)
    user2 = UserFactory(tenant=tenant2)
    tenant2.owner = user2

    rule1 = Rule[User]("is_member", is_member)
    rule2 = Rule[User]("is_owner", is_owner)

    assert (await rule1.inspect(user1, tenant1, "blbl")).allowed()
    assert (
        await rule1.inspect(user2, tenant1, {"test": 1})
    ).message() == "Unauthorized"
    assert (await rule2.inspect(user2, tenant2)).allowed()
    assert (await rule2.inspect(user1, tenant2)).message() == "Not owner on the tenant"
